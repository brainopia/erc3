from erc3_live.aggregate import aggregate_results
from erc3_live.models import PublicTaskResult, PublicTaskRun, PublicTaskSpec, TaskRuntimeInfo


def make_result(status: str, score: float | None):
    spec = PublicTaskSpec(benchmark_id="erc3-prod", spec_id="t000", prompt="x", runs=1)
    runtime = TaskRuntimeInfo(benchmark_id="erc3-prod", spec_id="t000", task_id="tsk-1", task_url="https://example/tasks/tsk-1", api_root=None)
    return PublicTaskResult(spec=spec, runtime=runtime, status=status, score=score, logs="", duration_seconds=1.0)


def test_aggregate_results():
    summary = aggregate_results([make_result("completed", 1.0), make_result("agent_failed", 0.0)])
    assert summary.attempted == 2
    assert summary.completed == 1
    assert summary.failed == 1
    assert summary.total_score == 1.0
    assert summary.average_score == 0.5
