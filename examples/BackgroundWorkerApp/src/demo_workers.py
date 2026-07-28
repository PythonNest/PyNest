import logging

from nest.core import (
    BackgroundWorker,
    Injectable,
    IntervalWorker,
    RestartPolicy,
)

from .demo_service import DemoState

logger = logging.getLogger("uvicorn.error")


@Injectable
class QueueWorker(BackgroundWorker):
    """Consumes API-submitted jobs and calculates their squares."""

    name = "queue-processor"

    def __init__(self, state: DemoState):
        self.state = state

    async def on_start(self) -> None:
        self.state.record_lifecycle(f"{self.name}:start")

    async def run(self) -> None:
        while not self.stopping.is_set():
            job_id = await self.state.next_job(timeout=0.05)
            if job_id is None:
                continue
            await self.state.process(job_id)

    async def on_stop(self) -> None:
        self.state.record_lifecycle(f"{self.name}:stop")


@Injectable
class HeartbeatWorker(IntervalWorker):
    """Demonstrates non-overlapping fixed-delay interval work."""

    name = "heartbeat"
    interval = 0.02
    run_immediately = True

    def __init__(self, state: DemoState):
        self.state = state

    async def on_start(self) -> None:
        self.state.record_lifecycle(f"{self.name}:start")

    async def execute(self) -> None:
        heartbeat = self.state.record_heartbeat()
        if heartbeat == 1 or heartbeat % 50 == 0:
            logger.info("Heartbeat worker is alive (heartbeat=%d)", heartbeat)

    async def on_stop(self) -> None:
        self.state.record_lifecycle(f"{self.name}:stop")


@Injectable
class ResilientWorker(BackgroundWorker):
    """Fails once so the supervisor's successful restart is visible."""

    name = "resilient"
    restart = RestartPolicy.ON_FAILURE
    restart_backoff = 0.01
    restart_backoff_max = 0.01

    def __init__(self, state: DemoState):
        self.state = state
        self.attempts = 0

    async def on_start(self) -> None:
        self.state.record_lifecycle(f"{self.name}:start")

    async def run(self) -> None:
        self.attempts += 1
        if self.attempts == 1:
            raise RuntimeError("intentional first-run failure")

        self.state.mark_resilient_worker_recovered()
        await self.stopping.wait()

    async def on_stop(self) -> None:
        self.state.record_lifecycle(f"{self.name}:stop")
