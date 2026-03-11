from __future__ import annotations

from erc3_live.tests.e2e_helpers import (
    DEFAULT_BENCHMARK,
    DEFAULT_SPEC_ID,
    assert_task_specs_shape,
    dispatch_snapshot,
    managed_public_task,
    require_live_e2e,
)


def test_live_public_listing() -> None:
    require_live_e2e()
    from erc3_live.transport import LiveTransport

    transport = LiveTransport()
    try:
        tasks = transport.list_public_tasks(DEFAULT_BENCHMARK)
        assert_task_specs_shape(tasks)
        assert any(task.spec_id == DEFAULT_SPEC_ID for task in tasks), (
            f"expected default spec {DEFAULT_SPEC_ID} to be listed; got sample {[task.spec_id for task in tasks[:10]]}"
        )
    finally:
        transport.close()


def test_live_sdk_task_flow() -> None:
    require_live_e2e()
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

        assert run.runtime.task_id.startswith("tsk-"), run.runtime.task_id
        assert run.runtime.task_url.endswith(run.runtime.task_id), run.runtime.task_url
        assert isinstance(run.runtime.api_root, str) and run.runtime.api_root, metadata
        assert metadata.get("task_id") == run.runtime.task_id, metadata
        assert metadata.get("api_root") == run.runtime.api_root, metadata

        who_am_i_snapshot = dispatch_snapshot(who_am_i)
        projects_snapshot = dispatch_snapshot(projects)
        respond_snapshot = dispatch_snapshot(respond)

        for snapshot, endpoint in (
            (who_am_i_snapshot, "/whoami"),
            (projects_snapshot, "/projects/list"),
            (respond_snapshot, "/respond"),
        ):
            assert snapshot["via"] in {"http", "browser"}, snapshot
            assert snapshot["path"] == f"/{run.runtime.api_root}/{run.runtime.task_id}{endpoint}", snapshot
            assert isinstance(snapshot["payload"], dict), snapshot

        assert who_am_i_snapshot["payload"], who_am_i_snapshot
        assert projects_snapshot["payload"], projects_snapshot
        assert respond_snapshot["path"].endswith("/respond"), respond_snapshot
