from __future__ import annotations

from typing import Any


def run_agent(task_client: Any, task_info: Any) -> None:
    task_client.who_am_i()
    raise RuntimeError(f"intentional failure for {task_info.runtime.task_id}")
