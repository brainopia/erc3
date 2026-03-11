from __future__ import annotations

from erc3_live.tests.e2e_helpers import (
    DEFAULT_BENCHMARK,
    DEFAULT_SPEC_ID,
    MINIMAL_AGENT,
    DEFAULT_LIST_MIN_COUNT,
    run_cli_json,
    require_live_e2e,
)


def test_live_cli_list_tasks() -> None:
    require_live_e2e()
    payload = run_cli_json("list-tasks", "--benchmark", DEFAULT_BENCHMARK)
    assert isinstance(payload, list), payload
    assert len(payload) >= DEFAULT_LIST_MIN_COUNT, len(payload)
    first = payload[0]
    assert first["benchmark_id"] == DEFAULT_BENCHMARK, first
    assert isinstance(first["spec_id"], str) and first["spec_id"].startswith("t"), first
    assert any(item["spec_id"] == DEFAULT_SPEC_ID for item in payload), DEFAULT_SPEC_ID


def test_live_cli_run_task() -> None:
    require_live_e2e()
    payload = run_cli_json(
        "run-task",
        "--benchmark",
        DEFAULT_BENCHMARK,
        "--spec",
        DEFAULT_SPEC_ID,
        "--agent",
        str(MINIMAL_AGENT),
    )
    assert payload["spec"]["spec_id"] == DEFAULT_SPEC_ID, payload
    assert payload["runtime"]["task_id"].startswith("tsk-"), payload
    assert payload["runtime"]["api_root"], payload
    assert payload["status"] in {"completed", "agent_failed"}, payload
    assert payload["metadata"]["completion_status"] in {"completed", "already_completed"}, payload
    assert payload["metadata"]["dispatch_via"] in {"http", "browser"}, payload
    assert isinstance(payload["score"], (int, float)), payload
    assert isinstance(payload["logs"], str), payload
