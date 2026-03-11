from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erc3_live.client import TaskClient
from erc3_live.tests.e2e_helpers import DEFAULT_BENCHMARK, DEFAULT_SPEC_ID, assert_task_specs_shape, dispatch_snapshot
from erc3_live.transport import LiveTransport


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    benchmark = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BENCHMARK
    spec_id = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SPEC_ID
    transport = LiveTransport()
    run = None
    completion_payload: dict[str, object] | None = None
    try:
        tasks = transport.list_public_tasks(benchmark)
        assert_task_specs_shape(tasks)
        ensure(any(task.spec_id == spec_id for task in tasks), f"spec {spec_id} not found in listed tasks")

        run = transport.start_public_task(benchmark, spec_id)
        client = TaskClient(transport, run)
        metadata = transport.get_task_page_metadata(run.runtime.task_id)
        who_am_i = client.dispatch("/whoami", {})
        read_only_endpoint = "/projects/list"
        read_only_payload = client.dispatch(read_only_endpoint, {})
        respond_payload = client.dispatch(
            "/respond",
            {
                "message": f"Live probe for {run.runtime.task_id}",
                "outcome": "clarifying_question",
                "links": [],
            },
        )

        ensure(run.runtime.task_id.startswith("tsk-"), f"unexpected task id: {run.runtime.task_id}")
        ensure(bool(run.runtime.api_root), f"missing api_root in runtime: {metadata}")
        ensure(metadata.get("task_id") == run.runtime.task_id, f"task metadata mismatch: {metadata}")
        ensure(metadata.get("api_root") == run.runtime.api_root, f"api_root metadata mismatch: {metadata}")

        for endpoint, snapshot in (
            ("/whoami", dispatch_snapshot(who_am_i)),
            (read_only_endpoint, dispatch_snapshot(read_only_payload)),
            ("/respond", dispatch_snapshot(respond_payload)),
        ):
            expected_path = f"/{run.runtime.api_root}/{run.runtime.task_id}{endpoint}"
            ensure(snapshot["via"] in {"http", "browser"}, f"unexpected dispatch mode for {endpoint}: {snapshot}")
            ensure(snapshot["path"] == expected_path, f"unexpected dispatch path for {endpoint}: {snapshot}")
            ensure(isinstance(snapshot["payload"], dict), f"non-object payload for {endpoint}: {snapshot}")
            if endpoint != "/respond":
                ensure(bool(snapshot["payload"]), f"empty payload for {endpoint}: {snapshot}")

        completion = transport.complete_task(run.runtime.task_id)
        completion_payload = {
            "status": completion.status,
            "score": completion.score,
            "logs": completion.logs,
            "raw": completion.raw,
        }

        print(
            json.dumps(
                {
                    "benchmark": benchmark,
                    "task_count": len(tasks),
                    "spec_id": spec_id,
                    "task_id": run.runtime.task_id,
                    "task_url": run.runtime.task_url,
                    "api_root": run.runtime.api_root,
                    "task_metadata": metadata,
                    "who_am_i": dispatch_snapshot(who_am_i),
                    "read_only": {
                        "endpoint": read_only_endpoint,
                        **dispatch_snapshot(read_only_payload),
                    },
                    "respond": dispatch_snapshot(respond_payload),
                    "completion": completion_payload,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    finally:
        if run is not None and completion_payload is None:
            try:
                transport.complete_task(run.runtime.task_id)
            except Exception:
                pass
        transport.close()


if __name__ == "__main__":
    raise SystemExit(main())
