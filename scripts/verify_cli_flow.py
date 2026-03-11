from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_BENCHMARK = "erc3-prod"
DEFAULT_SPEC_ID = "t025"
MIN_LIST_COUNT = 50
MINIMAL_AGENT = ROOT / "examples" / "minimal_agent.py"


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_cli(*args: str) -> Any:
    command = [sys.executable, "-m", "erc3_live.cli", *args]
    completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    ensure(
        completed.returncode == 0,
        f"CLI command failed: {' '.join(command)}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
    )
    return json.loads(completed.stdout)


def main() -> int:
    benchmark = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BENCHMARK
    spec_id = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SPEC_ID

    listed = run_cli("list-tasks", "--benchmark", benchmark)
    ensure(isinstance(listed, list), f"list-tasks did not return a list: {listed!r}")
    ensure(len(listed) >= MIN_LIST_COUNT, f"expected at least {MIN_LIST_COUNT} listed tasks, got {len(listed)}")
    ensure(any(item.get("spec_id") == spec_id for item in listed), f"spec {spec_id} not present in list output")

    run_result = run_cli(
        "run-task",
        "--benchmark",
        benchmark,
        "--spec",
        spec_id,
        "--agent",
        str(MINIMAL_AGENT),
    )
    runtime = run_result.get("runtime", {})
    metadata = run_result.get("metadata", {})

    ensure(run_result.get("spec", {}).get("spec_id") == spec_id, f"unexpected run-task spec: {run_result}")
    ensure(str(runtime.get("task_id", "")).startswith("tsk-"), f"unexpected task id: {run_result}")
    ensure(bool(runtime.get("api_root")), f"missing api_root: {run_result}")
    ensure(metadata.get("completion_status") in {"completed", "already_completed"}, f"unexpected completion status: {run_result}")
    ensure(metadata.get("dispatch_via") == "http", f"unexpected dispatch transport metadata: {run_result}")
    ensure(run_result.get("status") == "completed", f"unexpected runner status: {run_result}")
    ensure(isinstance(run_result.get("score"), (int, float)), f"missing score: {run_result}")
    ensure(isinstance(run_result.get("logs"), str), f"missing logs: {run_result}")

    print(
        json.dumps(
            {
                "benchmark": benchmark,
                "spec_id": spec_id,
                "list_tasks": {
                    "count": len(listed),
                    "sample_spec_ids": [item["spec_id"] for item in listed[:10]],
                },
                "run_task": run_result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
