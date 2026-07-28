from fastapi import FastAPI

from nest.core import Module, PyNestApp, PyNestFactory

from .additional_workers import (
    CacheRefreshWorker,
    DataSyncWorker,
    MetricsFlushWorker,
    ReportGenerationWorker,
    SessionCleanupWorker,
)
from .app_controller import AppController
from .demo_service import DemoState, WorkerStatusService
from .demo_workers import HeartbeatWorker, QueueWorker, ResilientWorker


@Module(
    controllers=[AppController],
    providers=[
        DemoState,
        WorkerStatusService,
        QueueWorker,
        HeartbeatWorker,
        ResilientWorker,
        CacheRefreshWorker,
        MetricsFlushWorker,
        SessionCleanupWorker,
        ReportGenerationWorker,
        DataSyncWorker,
    ],
)
class AppModule:
    pass


def create_app() -> PyNestApp:
    pynest_app = PyNestFactory.create(
        AppModule,
        title="PyNest Background Worker Demo",
        description=(
            "Demonstrates injected queue processing, interval jobs, "
            "restart-on-failure supervision, and graceful shutdown."
        ),
        version="1.0.0",
        worker_grace_timeout=1.0,
    )
    status_service = pynest_app.container.get(WorkerStatusService)
    status_service.bind(pynest_app.get_worker_host())
    return pynest_app


app = create_app()
http_server: FastAPI = app.get_server()
