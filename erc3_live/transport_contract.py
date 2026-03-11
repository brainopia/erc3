"""Observed ERC3 public-task transport contract.

Verified against the live public site on 2026-03-11:
- POST /tasks/start with {benchmark, spec_id} starts an anonymous public task and returns a task_id like tsk-...
- GET /tasks/<task_id> returns an HTML task page containing:
  - window.currentTaskID
  - window.apiRoot (observed value: erc3-dev)
  - UI code that calls erc32.dispatch(window.apiRoot, window.currentTaskID, endpoint, body)
  - sample curl commands constructed as /<api_root>/<task_id>/<endpoint>
- assets/client.js defines dispatch(benchmarkId, taskId, routePath, body) as POST /<benchmarkId>/<taskId><routePath>
- Task-local API calls therefore use HTTP JSON POST requests to /<api_root>/<task_id>/<endpoint>
- Task-local requests fail directly on HTTP transport errors; there is no browser fallback path
- POST /tasks/complete with {task_id} returns JSON including eval.score and eval.logs
- No login cookie or CSRF token was required for verified anonymous start and complete flow

This module exists as a checked-in technical note to satisfy phase-1 verification.
"""
