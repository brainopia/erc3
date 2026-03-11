from __future__ import annotations

from erc3_live.tests.e2e.helpers import (
    DEFAULT_BENCHMARK,
    DEFAULT_MATRIX_SPEC_IDS,
    DEFAULT_SPEC_ID,
    assert_completion_shape,
    assert_http_dispatch,
    assert_task_specs_shape,
    dispatch_snapshot,
    managed_public_task,
)
from erc3_live.transport import LiveTransport


def test_live_public_listing() -> None:
    transport = LiveTransport()
    try:
        tasks = transport.list_public_tasks(DEFAULT_BENCHMARK)
        assert_task_specs_shape(tasks)
        listed_spec_ids = {task.spec_id for task in tasks}
        assert DEFAULT_SPEC_ID in listed_spec_ids, listed_spec_ids
        assert set(DEFAULT_MATRIX_SPEC_IDS).issubset(listed_spec_ids), listed_spec_ids
    finally:
        transport.close()


def test_live_repeated_start_returns_unique_task_ids() -> None:
    transport = LiveTransport()
    runs = []
    completions = []
    try:
        for _ in range(2):
            run = transport.start_public_task(DEFAULT_BENCHMARK, DEFAULT_SPEC_ID)
            runs.append(run)
            assert run.runtime.task_id.startswith("tsk-"), run
            assert run.runtime.task_url.endswith(run.runtime.task_id), run
            assert run.runtime.api_root, run
            completions.append(transport.complete_task(run.runtime.task_id))
        task_ids = {run.runtime.task_id for run in runs}
        assert len(task_ids) == 2, runs
        for run, completion in zip(runs, completions, strict=True):
            assert run.runtime.benchmark_id == DEFAULT_BENCHMARK, run
            assert run.runtime.spec_id == DEFAULT_SPEC_ID, run
            assert_completion_shape(completion)
    finally:
        transport.close()


def test_live_sdk_task_flow() -> None:
    with managed_public_task() as (core, run, client):
        metadata = core.transport.get_task_page_metadata(run.runtime.task_id)
        who_am_i = client.dispatch("/whoami", {})
        projects = client.dispatch("/projects/list", {})
        respond = client.dispatch(
            "/respond",
            {
                "message": f"Live E2E probe for {run.runtime.task_id}",
                "outcome": "clarifying_question",
                "links": [],
            },
        )

        assert metadata.get("task_id") == run.runtime.task_id, metadata
        assert metadata.get("api_root") == run.runtime.api_root, metadata

        who_am_i_snapshot = dispatch_snapshot(who_am_i)
        projects_snapshot = dispatch_snapshot(projects)
        respond_snapshot = dispatch_snapshot(respond)

        assert_http_dispatch(who_am_i_snapshot, api_root=run.runtime.api_root or "", task_id=run.runtime.task_id, endpoint="/whoami")
        assert_http_dispatch(projects_snapshot, api_root=run.runtime.api_root or "", task_id=run.runtime.task_id, endpoint="/projects/list")
        assert_http_dispatch(respond_snapshot, api_root=run.runtime.api_root or "", task_id=run.runtime.task_id, endpoint="/respond")

        assert who_am_i_snapshot["payload"], who_am_i_snapshot
        assert projects_snapshot["payload"], projects_snapshot
        assert respond_snapshot["payload"] == {} or respond_snapshot["payload"], respond_snapshot


def test_live_spec_matrix_read_only_flow() -> None:
    transport = LiveTransport()
    started_task_ids: list[str] = []
    completions = []
    try:
        for spec_id in DEFAULT_MATRIX_SPEC_IDS:
            run = transport.start_public_task(DEFAULT_BENCHMARK, spec_id)
            started_task_ids.append(run.runtime.task_id)
            metadata = transport.get_task_page_metadata(run.runtime.task_id)
            response = transport.dispatch(run.runtime, "/whoami", {})
            snapshot = dispatch_snapshot(response)
            assert metadata.get("task_id") == run.runtime.task_id, metadata
            assert metadata.get("api_root") == run.runtime.api_root, metadata
            assert_http_dispatch(snapshot, api_root=run.runtime.api_root or "", task_id=run.runtime.task_id, endpoint="/whoami")
            assert snapshot["payload"], snapshot
            completions.append(transport.complete_task(run.runtime.task_id))
        assert len(started_task_ids) == len(set(started_task_ids)), started_task_ids
        for completion in completions:
            assert_completion_shape(completion)
    finally:
        transport.close()
