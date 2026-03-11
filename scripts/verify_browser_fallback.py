from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erc3_live.client import TaskClient
from erc3_live.tests.live_fallback_runtime import ForcedFallbackBrowserRuntime
from erc3_live.transport import LiveTransport

DEFAULT_BENCHMARK = "erc3-prod"
DEFAULT_SPEC_ID = "t025"


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    benchmark = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BENCHMARK
    spec_id = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SPEC_ID
    transport = LiveTransport()
    run = None
    completion_attempted = False
    try:
        run = transport.start_public_task(benchmark, spec_id)
        client = TaskClient(transport, run)
        fail_path = f"/{run.runtime.api_root}/{run.runtime.task_id}/whoami"
        forced_runtime = ForcedFallbackBrowserRuntime(transport.runtime, fail_path=fail_path)
        transport.runtime = forced_runtime
        try:
            result = client.dispatch("/whoami", {})
        finally:
            transport.runtime = forced_runtime.inner
        completion = transport.complete_task(run.runtime.task_id)
        completion_attempted = True

        ensure(forced_runtime.forced_http_failures == 1, f"expected one forced HTTP failure, got {forced_runtime}")
        ensure(forced_runtime.browser_calls == [
            {
                "task_url": run.runtime.task_url,
                "api_root": run.runtime.api_root,
                "task_id": run.runtime.task_id,
                "route_path": "/whoami",
                "body": {},
            }
        ], f"unexpected browser dispatch args: {forced_runtime.browser_calls}")
        ensure(result.via == "browser", f"fallback did not switch to browser mode: {result}")
        ensure(result.path == fail_path, f"unexpected fallback path: {result}")
        ensure(isinstance(result.payload, dict) and result.payload, f"unexpected fallback payload: {result}")

        print(
            json.dumps(
                {
                    "benchmark": benchmark,
                    "spec_id": spec_id,
                    "task_id": run.runtime.task_id,
                    "api_root": run.runtime.api_root,
                    "dispatch": {
                        "via": result.via,
                        "path": result.path,
                        "payload": result.payload,
                    },
                    "browser_dispatch_call": forced_runtime.browser_calls[0],
                    "completion": {
                        "status": completion.status,
                        "score": completion.score,
                        "logs": completion.logs,
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    finally:
        if run is not None and not completion_attempted:
            try:
                transport.complete_task(run.runtime.task_id)
            except Exception:
                pass
        transport.close()


if __name__ == "__main__":
    raise SystemExit(main())
