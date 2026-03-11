from __future__ import annotations

from typing import Any


def run_agent(task_client: Any, task_info: Any) -> dict[str, Any]:
    identity = task_client.who_am_i()
    projects = task_client.request("/projects/list", {})
    task_client.respond(
        message=f"Task {task_info.runtime.task_id} via {task_info.runtime.dispatch_via or 'unknown'}",
        outcome="clarifying_question",
        links=[],
    )
    return {"identity": identity, "projects": projects}


def failing_agent(task_client: Any, task_info: Any) -> None:
    task_client.who_am_i()
    raise RuntimeError(f"intentional failure for {task_info.runtime.task_id}")

def solve(task_info: Any, client: Any) -> dict[str, Any]:
    return run_agent(client, task_info)
