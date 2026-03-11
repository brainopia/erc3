from erc3_live.parsing import parse_completion_response, parse_public_task_specs, parse_task_page_metadata


def test_parse_public_task_specs():
    html = '''<tr><td class="col-id"><code class="font-mono text-xs">t000</code></td><td><div class="text-sm">Prompt</div><div class="task-hint">Warn</div></td><td class="col-agent-runs">123</td></tr>'''
    specs = parse_public_task_specs(html, "erc3-prod")
    assert len(specs) == 1
    assert specs[0].spec_id == "t000"
    assert specs[0].prompt == "Prompt"
    assert specs[0].warning == "Warn"
    assert specs[0].runs == 123


def test_parse_task_page_metadata():
    html = '''<h3>Task <span class="benchmark-name">erc3-prod</span>/t000</h3><span class="status status-in_progress">in_progress</span><script>window.currentTaskID = 'tsk-123'; window.apiRoot = 'erc3-dev'; async function sendAPIRequest() { return await erc32.dispatch(window.apiRoot, window.currentTaskID, endpoint, body); }</script>{"CurlCommand": "curl -X POST https://erc.timetoact-group.at/erc3-dev/tsk-123/whoami"}'''
    meta = parse_task_page_metadata(html)
    assert meta["task_id"] == "tsk-123"
    assert meta["benchmark_id"] == "erc3-prod"
    assert meta["spec_id"] == "t000"
    assert meta["status"] == "in_progress"
    assert meta["api_root"] == "erc3-dev"
    assert meta["sample_curl"].endswith('/erc3-dev/tsk-123/whoami')
    assert meta["uses_ui_dispatch"] == "true"


def test_parse_completion_response():
    status, score, logs = parse_completion_response({"status": "completed", "eval": {"score": 0.5, "logs": "ok"}})
    assert status == "completed"
    assert score == 0.5
    assert logs == "ok"
