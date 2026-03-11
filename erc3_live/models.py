from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class PublicTaskSpec:
    benchmark_id: str
    spec_id: str
    prompt: str
    runs: int
    warning: str | None = None


@dataclass(slots=True)
class TaskRuntimeInfo:
    benchmark_id: str
    spec_id: str
    task_id: str
    task_url: str
    api_root: str | None
    started_at: datetime | None = None
    dispatch_via: str | None = None


@dataclass(slots=True)
class DispatchResult:
    payload: dict[str, Any]
    via: str
    path: str


@dataclass(slots=True)
class TaskCompletion:
    status: str
    score: float
    logs: str
    raw: dict[str, Any]

@dataclass(slots=True)
class PublicTaskRun:
    spec: PublicTaskSpec
    runtime: TaskRuntimeInfo


@dataclass(slots=True)
class PublicTaskResult:
    spec: PublicTaskSpec
    runtime: TaskRuntimeInfo
    status: str
    score: float | None
    logs: str
    duration_seconds: float
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AggregateSummary:
    attempted: int
    completed: int
    failed: int
    total_score: float
    average_score: float
    success_rate: float
    by_status: dict[str, int]
    raw_scores: list[float]
