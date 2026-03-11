from __future__ import annotations

from collections import Counter

from .models import AggregateSummary, PublicTaskResult


def aggregate_results(results: list[PublicTaskResult]) -> AggregateSummary:
    attempted = len(results)
    completed_results = [result for result in results if result.score is not None]
    raw_scores = [float(result.score) for result in completed_results if result.score is not None]
    by_status = Counter(result.status for result in results)
    completed = sum(1 for result in results if result.status == "completed")
    failed = attempted - completed
    total_score = sum(raw_scores)
    average_score = total_score / len(raw_scores) if raw_scores else 0.0
    success_rate = completed / attempted if attempted else 0.0
    return AggregateSummary(
        attempted=attempted,
        completed=completed,
        failed=failed,
        total_score=total_score,
        average_score=average_score,
        success_rate=success_rate,
        by_status=dict(by_status),
        raw_scores=raw_scores,
    )


def summarize_results(results: list[PublicTaskResult]) -> dict[str, object]:
    summary = aggregate_results(results)
    return {
        "attempted": summary.attempted,
        "completed": summary.completed,
        "failed": summary.failed,
        "total_score": summary.total_score,
        "average_score": summary.average_score,
        "success_rate": summary.success_rate,
        "by_status": summary.by_status,
    }
