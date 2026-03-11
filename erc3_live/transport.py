from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests

from .browser_runtime import BrowserRuntime
from .errors import ParseError, TaskStateError, TransportError
from .models import DispatchResult, PublicTaskRun, PublicTaskSpec, TaskCompletion, TaskRuntimeInfo
from .parsing import parse_completion_response, parse_public_task_specs, parse_task_page_metadata


class LiveTransport:
    def __init__(self, base_url: str = "https://erc.timetoact-group.at", session: requests.Session | None = None) -> None:
        self.runtime = BrowserRuntime(session=session or requests.Session(), base_url=base_url)
        self.runtime.session.headers.update({"User-Agent": self.runtime.user_agent})

    def close(self) -> None:
        self.runtime.close()

    def list_public_tasks(self, benchmark_id: str) -> list[PublicTaskSpec]:
        html = self.runtime.fetch_text(f"/benchmarks/{benchmark_id}")
        return parse_public_task_specs(html, benchmark_id)

    def start_public_task(self, benchmark_id: str, spec_id: str) -> PublicTaskRun:
        payload = self.runtime.post_json("/tasks/start", {"benchmark": benchmark_id, "spec_id": spec_id})
        task_id = payload.get("task_id")
        if not isinstance(task_id, str) or not task_id.startswith("tsk-"):
            raise ParseError(f"Unexpected start response: {payload!r}")
        page_html = self.runtime.fetch_text(f"/tasks/{task_id}")
        meta = parse_task_page_metadata(page_html)
        runtime = TaskRuntimeInfo(
            benchmark_id=benchmark_id,
            spec_id=spec_id,
            task_id=task_id,
            task_url=f"{self.runtime.base_url}/tasks/{task_id}",
            api_root=meta.get("api_root"),
            started_at=datetime.now(timezone.utc),
        )
        spec = PublicTaskSpec(
            benchmark_id=benchmark_id,
            spec_id=spec_id,
            prompt=str(payload.get("text", "")),
            runs=0,
        )
        return PublicTaskRun(spec=spec, runtime=runtime)

    def get_task_page_metadata(self, task_id: str) -> dict[str, str | None]:
        page_html = self.runtime.fetch_text(f"/tasks/{task_id}")
        return parse_task_page_metadata(page_html)

    def dispatch(self, runtime: TaskRuntimeInfo, route_path: str, body: dict[str, Any] | None = None) -> DispatchResult:
        normalized_route = route_path if route_path.startswith("/") else f"/{route_path}"
        payload = body or {}
        api_root = runtime.api_root
        if not api_root:
            raise TransportError(f"Task {runtime.task_id} is missing api_root; cannot dispatch {normalized_route}")

        http_path = f"/{api_root}/{runtime.task_id}{normalized_route}"
        try:
            response = self.runtime.post_json(http_path, payload)
            runtime.dispatch_via = "http"
            return DispatchResult(payload=response, via="http", path=http_path)
        except TransportError as http_exc:
            response = self.runtime.dispatch_via_browser(
                task_url=runtime.task_url,
                api_root=api_root,
                task_id=runtime.task_id,
                route_path=normalized_route,
                body=payload,
            )
            runtime.dispatch_via = "browser"
            return DispatchResult(payload=response, via="browser", path=http_path) if response else self._browser_failure(http_path, http_exc)

    def complete_task(self, task_id: str) -> TaskCompletion:
        payload = self.runtime.post_json("/tasks/complete", {"task_id": task_id})
        status, score, logs = parse_completion_response(payload)
        if status not in {"completed", "already_completed"}:
            raise TaskStateError(f"Unexpected task completion status: {status}")
        return TaskCompletion(status=status, score=score, logs=logs, raw=payload)

    @staticmethod
    def _browser_failure(http_path: str, http_exc: TransportError) -> DispatchResult:
        raise TransportError(f"Task endpoint failed for {http_path}; HTTP error: {http_exc}")
