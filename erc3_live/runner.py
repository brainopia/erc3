from __future__ import annotations

import importlib.util
import time
from pathlib import Path
from typing import Callable

from .client import TaskClient
from .errors import AgentExecutionError
from .models import PublicTaskResult, PublicTaskRun
from .public_sdk import PublicERC3

AgentCallable = Callable[[TaskClient, PublicTaskRun], None]


def load_agent_callable(agent_path: str) -> AgentCallable:
    path = Path(agent_path)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise AgentExecutionError(f"Failed to load agent module from {agent_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    run_agent = getattr(module, "run_agent", None)
    if callable(run_agent):
        return run_agent
    solve = getattr(module, "solve", None)
    if callable(solve):
        return lambda task_client, task_info: solve(task_info, task_client)
    raise AgentExecutionError("Agent module must expose run_agent(task_client, task_info) or solve(task_info, client)")


def run_task_with_agent(core: PublicERC3, benchmark_id: str, spec_id: str, agent: AgentCallable) -> PublicTaskResult:
    run = core.start_public_task(benchmark_id, spec_id)
    client = core.get_task_client(run)
    started = time.monotonic()
    try:
        agent(client, run)
    except Exception as exc:  # noqa: BLE001
        return core.complete_task(run, started=started, error=f"agent failed: {exc}")
    return core.complete_task(run, started=started)


def run_many(core: PublicERC3, benchmark_id: str, agent: AgentCallable, spec_ids: list[str] | None = None) -> list[PublicTaskResult]:
    specs = core.list_public_tasks(benchmark_id)
    selected = [spec for spec in specs if spec_ids is None or spec.spec_id in spec_ids]
    results: list[PublicTaskResult] = []
    for spec in selected:
        results.append(run_task_with_agent(core, benchmark_id, spec.spec_id, agent))
    return results
