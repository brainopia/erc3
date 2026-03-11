from __future__ import annotations

import json
import os
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterator

import pytest

from erc3_live.client import TaskClient
from erc3_live.public_sdk import PublicERC3
from erc3_live.transport import LiveTransport

DEFAULT_BENCHMARK = os.environ.get("ERC3_LIVE_BENCHMARK", "erc3-prod")
DEFAULT_SPEC_ID = os.environ.get("ERC3_LIVE_SPEC_ID", "t025")
DEFAULT_LIST_MIN_COUNT = int(os.environ.get("ERC3_LIVE_LIST_MIN_COUNT", "50"))
ROOT = Path(__file__).resolve().parents[2]
MINIMAL_AGENT = ROOT / "examples" / "minimal_agent.py"
RUN_LIVE_E2E = os.environ.get("ERC3_RUN_LIVE_E2E") == "1"


def require_live_e2e() -> None:
    if not RUN_LIVE_E2E:
        pytest.skip("live E2E tests are disabled; set ERC3_RUN_LIVE_E2E=1")


def assert_task_specs_shape(tasks: list[Any], *, min_count: int = DEFAULT_LIST_MIN_COUNT) -> None:
    assert len(tasks) >= min_count, f"expected at least {min_count} public tasks, got {len(tasks)}"
    for task in tasks[:5]:
        assert getattr(task, "benchmark_id", None) == DEFAULT_BENCHMARK, f"unexpected benchmark on task: {task!r}"
        spec_id = getattr(task, "spec_id", None)
        assert isinstance(spec_id, str) and spec_id.startswith("t"), f"unexpected spec id: {task!r}"
        prompt = getattr(task, "prompt", None)
        assert isinstance(prompt, str) and prompt.strip(), f"missing prompt: {task!r}"


@contextmanager
def managed_public_task(benchmark_id: str = DEFAULT_BENCHMARK, spec_id: str = DEFAULT_SPEC_ID) -> Iterator[tuple[PublicERC3, Any, TaskClient]]:
    core = PublicERC3()
    run = core.start_public_task(benchmark_id, spec_id)
    client = core.get_task_client(run)
    try:
        yield core, run, client
    finally:
        try:
            core.complete_task(run)
        except Exception:
            pass
        core.close()


def run_cli_json(*args: str) -> dict[str, Any] | list[dict[str, Any]]:
    command = [sys.executable, "-m", "erc3_live.cli", *args]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, (
        f"CLI command failed: {' '.join(command)}\n"
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
    )
    return json.loads(completed.stdout)


def dispatch_snapshot(result: Any) -> dict[str, Any]:
    payload = getattr(result, "payload", None)
    return {
        "via": getattr(result, "via", None),
        "path": getattr(result, "path", None),
        "payload": payload,
    }


def result_snapshot(result: Any) -> dict[str, Any]:
    return asdict(result)


@pytest.mark.live
def test_live_listing_smoke() -> None:
    require_live_e2e()
    transport = LiveTransport()
    try:
        tasks = transport.list_public_tasks(DEFAULT_BENCHMARK)
        assert_task_specs_shape(tasks)
    finally:
        transport.close()
