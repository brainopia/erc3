from __future__ import annotations

import time

from .aggregate import aggregate_results
from .client import TaskClient
from .models import AggregateSummary, PublicTaskResult, PublicTaskRun, PublicTaskSpec
from .transport import LiveTransport


class PublicERC3:
    def __init__(self, transport: LiveTransport | None = None) -> None:
        self.transport = transport or LiveTransport()

    def close(self) -> None:
        self.transport.close()

    def list_public_tasks(self, benchmark_id: str) -> list[PublicTaskSpec]:
        return self.transport.list_public_tasks(benchmark_id)

    def start_public_task(self, benchmark_id: str, spec_id: str) -> PublicTaskRun:
        run = self.transport.start_public_task(benchmark_id, spec_id)
        specs = {spec.spec_id: spec for spec in self.list_public_tasks(benchmark_id)}
        if spec_id in specs:
            run.spec = specs[spec_id]
        return run

    def get_task_client(self, run: PublicTaskRun) -> TaskClient:
        return TaskClient(self.transport, run)

    def complete_task(self, run: PublicTaskRun, started: float | None = None, error: str | None = None) -> PublicTaskResult:
        completion = self.transport.complete_task(run.runtime.task_id)
        duration = time.monotonic() - started if started is not None else 0.0
        status = "completed" if error is None else "agent_failed"
        return PublicTaskResult(
            spec=run.spec,
            runtime=run.runtime,
            status=status,
            score=completion.score,
            logs=completion.logs,
            duration_seconds=duration,
            error=error,
            metadata={
                "completion_status": completion.status,
                "dispatch_via": run.runtime.dispatch_via,
            },
        )

    def aggregate_results(self, results: list[PublicTaskResult]) -> AggregateSummary:
        return aggregate_results(results)
