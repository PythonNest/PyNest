from __future__ import annotations

import asyncio
from collections import Counter
from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from nest.core import Injectable, WorkerHost


@dataclass
class Job:
    id: str
    number: int
    status: str = "queued"
    result: Optional[int] = None

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "number": self.number,
            "status": self.status,
            "result": self.result,
        }


@Injectable
class DemoState:
    """In-memory state shared by the API and every demo worker."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._jobs: dict[str, Job] = {}
        self._heartbeats = 0
        self._resilient_worker_recovered = False
        self._lifecycle_events: list[str] = []
        self._background_task_runs: Counter[str] = Counter()

    @property
    def lifecycle_events(self) -> set[str]:
        return set(self._lifecycle_events)

    def submit(self, number: int) -> dict[str, object]:
        job = Job(id=uuid4().hex, number=number)
        self._jobs[job.id] = job
        self._queue.put_nowait(job.id)
        return job.as_dict()

    def get_job(self, job_id: str) -> Optional[dict[str, object]]:
        job = self._jobs.get(job_id)
        return job.as_dict() if job is not None else None

    async def next_job(self, timeout: float) -> Optional[str]:
        try:
            return await asyncio.wait_for(self._queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def process(self, job_id: str) -> None:
        job = self._jobs[job_id]
        job.status = "processing"
        try:
            await asyncio.sleep(0.01)
            job.result = job.number**2
            job.status = "completed"
        finally:
            self._queue.task_done()

    def record_heartbeat(self) -> int:
        self._heartbeats += 1
        return self._heartbeats

    def mark_resilient_worker_recovered(self) -> None:
        self._resilient_worker_recovered = True

    def record_lifecycle(self, event: str) -> None:
        self._lifecycle_events.append(event)

    def record_background_task(self, task_name: str) -> int:
        self._background_task_runs[task_name] += 1
        return self._background_task_runs[task_name]

    def summary(self) -> dict[str, object]:
        job_counts = Counter(job.status for job in self._jobs.values())
        return {
            "heartbeats": self._heartbeats,
            "resilient_worker_recovered": self._resilient_worker_recovered,
            "jobs": {
                "total": len(self._jobs),
                "queued": job_counts["queued"],
                "processing": job_counts["processing"],
                "completed": job_counts["completed"],
            },
            "background_tasks": dict(self._background_task_runs),
            "lifecycle_events": list(self._lifecycle_events),
        }


@Injectable
class WorkerStatusService:
    """Makes the app-local worker host available to the controller."""

    def __init__(self) -> None:
        self._host: Optional[WorkerHost] = None

    def bind(self, host: WorkerHost) -> None:
        self._host = host

    def status(self) -> list[dict[str, object]]:
        if self._host is None:
            raise RuntimeError("Worker status service has not been bound")
        return self._host.status()
