import logging

from nest.core import Injectable, IntervalWorker

from .demo_service import DemoState

logger = logging.getLogger("uvicorn.error")


@Injectable
class ObservableIntervalWorker(IntervalWorker):
    """Shared instrumentation for the five additional periodic tasks."""

    task_name = ""
    run_immediately = True

    def __init__(self, state: DemoState):
        self.state = state

    async def on_start(self) -> None:
        self.state.record_lifecycle(f"{self.name}:start")

    async def execute(self) -> None:
        run = self.state.record_background_task(self.task_name)
        logger.info(
            "Background task %s completed (run=%d)",
            self.task_name,
            run,
        )

    async def on_stop(self) -> None:
        self.state.record_lifecycle(f"{self.name}:stop")


@Injectable
class CacheRefreshWorker(ObservableIntervalWorker):
    name = "cache-refresh"
    task_name = "cache_refresh"
    interval = 2.0


@Injectable
class MetricsFlushWorker(ObservableIntervalWorker):
    name = "metrics-flush"
    task_name = "metrics_flush"
    interval = 3.0


@Injectable
class SessionCleanupWorker(ObservableIntervalWorker):
    name = "session-cleanup"
    task_name = "session_cleanup"
    interval = 4.0


@Injectable
class ReportGenerationWorker(ObservableIntervalWorker):
    name = "report-generation"
    task_name = "report_generation"
    interval = 5.0


@Injectable
class DataSyncWorker(ObservableIntervalWorker):
    name = "data-sync"
    task_name = "data_sync"
    interval = 6.0
