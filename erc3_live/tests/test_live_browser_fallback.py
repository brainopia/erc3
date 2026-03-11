from __future__ import annotations

import pytest

from erc3_live.tests.live_fallback_runtime import ForcedFallbackBrowserRuntime
from erc3_live.tests.e2e_helpers import managed_public_task, require_live_e2e


@pytest.mark.live
def test_live_browser_fallback_via_forced_http_failure() -> None:
    require_live_e2e()
    with managed_public_task() as (_, run, client):
        fail_path = f"/{run.runtime.api_root}/{run.runtime.task_id}/whoami"
        forced_runtime = ForcedFallbackBrowserRuntime(client.transport.runtime, fail_path=fail_path)
        client.transport.runtime = forced_runtime
        try:
            result = client.dispatch("/whoami", {})
        finally:
            client.transport.runtime = forced_runtime.inner

        assert forced_runtime.forced_http_failures == 1, forced_runtime
        assert forced_runtime.browser_calls == [
            {
                "task_url": run.runtime.task_url,
                "api_root": run.runtime.api_root,
                "task_id": run.runtime.task_id,
                "route_path": "/whoami",
                "body": {},
            }
        ], forced_runtime.browser_calls
        assert result.via == "browser", result
        assert result.path == fail_path, result
        assert isinstance(result.payload, dict) and result.payload, result
