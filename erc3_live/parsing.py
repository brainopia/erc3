from __future__ import annotations

import json
import re
from html import unescape

from .errors import ParseError
from .models import PublicTaskSpec


_TASK_ROW_RE = re.compile(
    r'<tr>\s*<td class="col-id"><code class="font-mono text-xs">(?P<spec>t\d{3}\s*)</code></td>'
    r'\s*<td>\s*<div class="text-sm">(?P<prompt>.*?)</div>'
    r'(?P<warning_block>.*?)</td>\s*<td[^>]*class="[^"]*col-agent-runs[^"]*"[^>]*>\s*(?P<runs>\d+)\s*</td>',
    re.DOTALL,
 )

_WARNING_RE = re.compile(
    r'<div[^>]*class="(?:task-hint|gotcha-warning|text-xs text-secondary)"[^>]*>\s*(?P<warning>.*?)\s*</div>',
    re.DOTALL,
 )
_TASK_ID_RE = re.compile(r"window\.currentTaskID\s*=\s*'(?P<task_id>tsk-[^']+)'")
_API_ROOT_RE = re.compile(r"window\.apiRoot\s*=\s*'(?P<api_root>[^']*)'")
_BENCHMARK_RE = re.compile(r"<h3[^>]*>Task <span class=\"benchmark-name\">(?P<benchmark>[^<]+)</span>/(?P<spec>t\d{3})</h3>")
_STATUS_RE = re.compile(r"<span class=\"status [^\"]+\">(?P<status>[^<]+)</span>")
_CURL_RE = re.compile(r'\"CurlCommand\":\s*\"(?P<curl>curl -X POST [^\"]+)\"')
_DISPATCH_CALL_RE = re.compile(
    r"erc32\.dispatch\(\s*window\.apiRoot\s*,\s*window\.currentTaskID\s*,\s*(?P<endpoint>[^,]+),\s*(?P<body>[^)]+)\)",
    re.DOTALL,
 )


def _clean_html_text(raw: str) -> str:
    text = re.sub(r"<[^>]+>", "", raw)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_public_task_specs(html: str, benchmark_id: str) -> list[PublicTaskSpec]:
    specs: list[PublicTaskSpec] = []
    for match in _TASK_ROW_RE.finditer(html):
        warning_match = _WARNING_RE.search(match.group("warning_block"))
        specs.append(
            PublicTaskSpec(
                benchmark_id=benchmark_id,
                spec_id=match.group("spec").strip(),
                prompt=_clean_html_text(match.group("prompt")),
                runs=int(match.group("runs")),
                warning=_clean_html_text(warning_match.group("warning")) if warning_match else None,
            )
        )
    if not specs:
        raise ParseError("Failed to parse public task specs from benchmark page")
    return specs


def parse_task_page_metadata(html: str) -> dict[str, str | None]:
    task_id_match = _TASK_ID_RE.search(html)
    benchmark_match = _BENCHMARK_RE.search(html)
    status_match = _STATUS_RE.search(html)
    api_root_match = _API_ROOT_RE.search(html)
    curl_match = _CURL_RE.search(html)
    dispatch_match = _DISPATCH_CALL_RE.search(html)
    if not task_id_match or not benchmark_match:
        raise ParseError("Failed to parse task page metadata")
    return {
        "task_id": task_id_match.group("task_id"),
        "benchmark_id": benchmark_match.group("benchmark").lower(),
        "spec_id": benchmark_match.group("spec"),
        "status": status_match.group("status") if status_match else None,
        "api_root": api_root_match.group("api_root") if api_root_match else None,
        "sample_curl": json.loads(f'"{curl_match.group("curl")}"') if curl_match else None,
        "uses_ui_dispatch": "true" if dispatch_match else "false",
    }


def parse_completion_response(payload: dict) -> tuple[str, float, str]:
    eval_payload = payload.get("eval") or {}
    score = float(eval_payload.get("score", 0.0))
    logs = str(eval_payload.get("logs", ""))
    status = str(payload.get("status", "completed"))
    return status, score, logs
