from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from erc3_live.browser_runtime import BrowserRuntime
from erc3_live.errors import TransportError


@dataclass(slots=True)
class ForcedFallbackBrowserRuntime:
    inner: BrowserRuntime
    fail_path: str
    browser_calls: list[dict[str, Any]] = field(default_factory=list)
    forced_http_failures: int = 0

    @property
    def base_url(self) -> str:
        return self.inner.base_url

    @property
    def user_agent(self) -> str:
        return self.inner.user_agent

    @property
    def session(self):
        return self.inner.session

    def fetch_text(self, path: str) -> str:
        return self.inner.fetch_text(path)

    def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if path == self.fail_path:
            self.forced_http_failures += 1
            raise TransportError("forced HTTP failure for browser fallback coverage")
        return self.inner.post_json(path, payload)

    def dispatch_via_browser(
        self,
        *,
        task_url: str,
        api_root: str,
        task_id: str,
        route_path: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        self.browser_calls.append(
            {
                "task_url": task_url,
                "api_root": api_root,
                "task_id": task_id,
                "route_path": route_path,
                "body": body,
            }
        )
        return self.inner.dispatch_via_browser(
            task_url=task_url,
            api_root=api_root,
            task_id=task_id,
            route_path=route_path,
            body=body,
        )

    def close(self) -> None:
        self.inner.close()
