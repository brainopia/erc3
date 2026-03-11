from __future__ import annotations

from erc3_live.tests.e2e.helpers import (
    AGENT_FIXTURES,
    DEFAULT_BENCHMARK,
    DEFAULT_LIST_MIN_COUNT,
    DEFAULT_SPEC_ID,
    MINIMAL_AGENT,
    run_cli_json,
)


def test_live_cli_list_tasks() -> None:
    payload = run_cli_json("list-tasks", "--benchmark", DEFAULT_BENCHMARK)
    assert isinstance(payload, list), payload
    assert len(payload) >= DEFAULT_LIST_MIN_COUNT, len(payload)
    first = payload[0]
    assert first["benchmark_id"] == DEFAULT_BENCHMARK, first
    assert isinstance(first["spec_id"], str) and first["spec_id"].startswith("t"), first
    assert any(item["spec_id"] == DEFAULT_SPEC_ID for item in payload), DEFAULT_SPEC_ID


def test_live_cli_run_task_success() -> None:
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
    assert payload["runtime"]["dispatch_via"] == "http", payload
    assert payload["status"] == "completed", payload
    assert payload["metadata"]["completion_status"] in {"completed", "already_completed"}, payload
    assert payload["metadata"]["dispatch_via"] == "http", payload
    assert isinstance(payload["duration_seconds"], (int, float)) and payload["duration_seconds"] >= 0, payload
    assert isinstance(payload["score"], (int, float)), payload
    assert isinstance(payload["logs"], str), payload
    assert payload.get("error") is None, payload


def test_live_cli_run_task_failure() -> None:
    payload = run_cli_json(
        "run-task",
        "--benchmark",
        DEFAULT_BENCHMARK,
        "--spec",
        DEFAULT_SPEC_ID,
        "--agent",
        str(AGENT_FIXTURES.with_name("failing_agent_fixture.py")),
    )
    assert payload["spec"]["spec_id"] == DEFAULT_SPEC_ID, payload
    assert payload["runtime"]["task_id"].startswith("tsk-"), payload
    assert payload["runtime"]["dispatch_via"] == "http", payload
    assert payload["status"] == "agent_failed", payload
    assert payload["metadata"]["completion_status"] in {"completed", "already_completed"}, payload
    assert payload["metadata"]["dispatch_via"] == "http", payload
    assert "intentional failure" in (payload.get("error") or ""), payload
    assert isinstance(payload["duration_seconds"], (int, float)) and payload["duration_seconds"] >= 0, payload
    assert isinstance(payload["score"], (int, float)), payload
    assert isinstance(payload["logs"], str), payload
