from __future__ import annotations

from erc3_live.public_sdk import PublicERC3
from erc3_live.runner import load_agent_callable, run_task_with_agent
from erc3_live.tests.e2e.helpers import AGENT_FIXTURES, DEFAULT_BENCHMARK, DEFAULT_SPEC_ID


def test_live_agent_request_response_flow_repeats() -> None:
    agent = load_agent_callable(str(AGENT_FIXTURES))
    core = PublicERC3()
    try:
        first = run_task_with_agent(core, DEFAULT_BENCHMARK, DEFAULT_SPEC_ID, agent)
        second = run_task_with_agent(core, DEFAULT_BENCHMARK, DEFAULT_SPEC_ID, agent)
    finally:
        core.close()

    for result in (first, second):
        assert result.spec.spec_id == DEFAULT_SPEC_ID, result
        assert result.runtime.task_id.startswith("tsk-"), result
        assert result.runtime.api_root, result
        assert result.runtime.dispatch_via == "http", result
        assert result.metadata["dispatch_via"] == "http", result
        assert result.metadata["completion_status"] in {"completed", "already_completed"}, result
        assert result.status == "completed", result
        assert isinstance(result.duration_seconds, float) and result.duration_seconds >= 0, result
        assert isinstance(result.logs, str), result
        assert isinstance(result.score, (int, float)), result
    assert first.runtime.task_id != second.runtime.task_id, (first, second)


def test_live_agent_failure_still_completes_task() -> None:
    agent = load_agent_callable(str(AGENT_FIXTURES.with_name("failing_agent_fixture.py")))
    core = PublicERC3()
    try:
        result = run_task_with_agent(core, DEFAULT_BENCHMARK, DEFAULT_SPEC_ID, agent)
    finally:
        core.close()

    assert result.spec.spec_id == DEFAULT_SPEC_ID, result
    assert result.runtime.task_id.startswith("tsk-"), result
    assert result.runtime.dispatch_via == "http", result
    assert result.metadata["dispatch_via"] == "http", result
    assert result.metadata["completion_status"] in {"completed", "already_completed"}, result
    assert result.status == "agent_failed", result
    assert "intentional failure" in (result.error or ""), result
    assert isinstance(result.duration_seconds, float) and result.duration_seconds >= 0, result
    assert isinstance(result.logs, str), result
    assert isinstance(result.score, (int, float)), result
