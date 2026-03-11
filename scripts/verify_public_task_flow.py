from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erc3_live.client import TaskClient
from erc3_live.transport import LiveTransport


def main() -> int:
    benchmark = sys.argv[1] if len(sys.argv) > 1 else "erc3-prod"
    spec_id = sys.argv[2] if len(sys.argv) > 2 else "t025"
    transport = LiveTransport()
    try:
        tasks = transport.list_public_tasks(benchmark)
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

        completion = transport.complete_task(run.runtime.task_id)
        print(
            json.dumps(
                {
                    "benchmark": benchmark,
                    "task_count": len(tasks),
                    "task_id": run.runtime.task_id,
                    "spec_id": spec_id,
                    "api_root": run.runtime.api_root,
                    "task_metadata": metadata,
                    "who_am_i": {
                        "via": who_am_i.via,
                        "path": who_am_i.path,
                        "payload": who_am_i.payload,
                    },
                    "read_only": {
                        "endpoint": read_only_endpoint,
                        "via": read_only_payload.via,
                        "path": read_only_payload.path,
                        "payload": read_only_payload.payload,
                    },
                    "respond": {
                        "via": respond_payload.via,
                        "path": respond_payload.path,
                        "payload": respond_payload.payload,
                    },
                    "completion_status": completion.status,
                    "score": completion.score,
                    "logs": completion.logs,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    finally:
        transport.close()


if __name__ == "__main__":
    raise SystemExit(main())
