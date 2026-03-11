from __future__ import annotations

from typing import Any

from .models import DispatchResult, PublicTaskRun
from .transport import LiveTransport


class TaskClient:
    def __init__(self, transport: LiveTransport, run: PublicTaskRun) -> None:
        self.transport = transport
        self.run = run

    def request(self, route_path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        result = self.dispatch(route_path, body)
        return result.payload

    def dispatch(self, route_path: str, body: dict[str, Any] | None = None) -> DispatchResult:
        return self.transport.dispatch(self.run.runtime, route_path, body)

    def who_am_i(self) -> dict[str, Any]:
        return self.request("/whoami", {})

    def respond(self, message: str, outcome: str = "ok_answer", links: list[dict[str, str]] | None = None) -> dict[str, Any]:
        return self.request(
            "/respond",
            {"message": message, "outcome": outcome, "links": links or []},
        )
