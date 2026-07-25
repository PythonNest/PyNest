import asyncio
import threading

import pytest
from fastapi.testclient import TestClient

from nest.common import OnApplicationBootstrap, OnModuleDestroy
from nest.common.background_worker import BackgroundWorker
from nest.core import Injectable, Module, PyNestFactory
from nest.core.worker_factory import WorkerAppFactory, run_workers


def test_http_lifespan_runs_workers_and_stops_them_before_provider_shutdown():
    events = []

    @Injectable
    class Dependency(OnModuleDestroy):
        def on_module_destroy(self) -> None:
            events.append("dependency:destroy")

    @Injectable
    class HttpWorker(BackgroundWorker):
        def __init__(self, dependency: Dependency):
            self.dependency = dependency
            self.started = threading.Event()

        async def run(self) -> None:
            events.append("worker:start")
            self.started.set()
            await self.stopping.wait()
            events.append("worker:exit")

        async def on_stop(self) -> None:
            events.append("worker:stop")

    @Module(providers=[HttpWorker, Dependency])
    class AppModule:
        pass

    app = PyNestFactory.create(AppModule)
    worker = app.container.get(HttpWorker)

    assert worker.dependency is app.container.get(Dependency)
    assert worker.started.is_set() is False

    with TestClient(app.get_server()):
        assert worker.started.wait(timeout=1)
        assert app.get_worker_host().status() == [
            {
                "name": "HttpWorker",
                "state": "running",
                "restarts": 0,
                "last_error": None,
            }
        ]

    assert events.index("worker:exit") < events.index("dependency:destroy")
    assert app.get_worker_host().status()[0]["state"] == "stopped"


def test_concurrent_http_close_callers_wait_for_the_same_shutdown():
    destroy_started = asyncio.Event()
    allow_destroy = asyncio.Event()

    @Injectable
    class SlowDependency(OnModuleDestroy):
        async def on_module_destroy(self) -> None:
            destroy_started.set()
            await allow_destroy.wait()

    @Module(providers=[SlowDependency])
    class AppModule:
        pass

    app = PyNestFactory.create(AppModule)

    async def scenario():
        first_close = asyncio.create_task(app.close())
        await asyncio.wait_for(destroy_started.wait(), timeout=0.1)
        second_close = asyncio.create_task(app.close())
        await asyncio.sleep(0)

        assert second_close.done() is False

        allow_destroy.set()
        await asyncio.gather(first_close, second_close)

    asyncio.run(scenario())


def test_standalone_app_runs_lifecycle_and_worker_on_one_loop():
    events = []
    loop_ids = []

    @Injectable
    class BootstrapProbe(OnApplicationBootstrap, OnModuleDestroy):
        async def on_application_bootstrap(self) -> None:
            events.append("bootstrap")
            loop_ids.append(id(asyncio.get_running_loop()))

        async def on_module_destroy(self) -> None:
            events.append("destroy")
            loop_ids.append(id(asyncio.get_running_loop()))

    @Injectable
    class CompletingWorker(BackgroundWorker):
        async def run(self) -> None:
            events.append("worker")
            loop_ids.append(id(asyncio.get_running_loop()))

    @Module(providers=[BootstrapProbe, CompletingWorker])
    class AppModule:
        pass

    async def scenario():
        app = WorkerAppFactory.create(AppModule, grace_timeout=0.1)

        await app.run()

        assert events == ["bootstrap", "worker", "destroy"]
        assert len(set(loop_ids)) == 1
        assert app.closed is True

    asyncio.run(scenario())


def test_standalone_request_shutdown_stops_a_long_running_worker():
    @Injectable
    class LongRunningWorker(BackgroundWorker):
        def __init__(self):
            self.started = asyncio.Event()
            self.exited = False

        async def run(self) -> None:
            self.started.set()
            await self.stopping.wait()
            self.exited = True

    @Module(providers=[LongRunningWorker])
    class AppModule:
        pass

    async def scenario():
        app = WorkerAppFactory.create(AppModule, grace_timeout=0.1)
        worker = app.container.get(LongRunningWorker)
        run_task = asyncio.create_task(app.run())
        await asyncio.wait_for(worker.started.wait(), timeout=0.1)

        app.request_shutdown("SIGTERM")
        await asyncio.wait_for(run_task, timeout=0.2)

        assert worker.exited is True
        assert app.signal == "SIGTERM"
        assert app.get_worker_host().status()[0]["state"] == "stopped"

    asyncio.run(scenario())


def test_standalone_close_is_idempotent():
    @Injectable
    class CompletingWorker(BackgroundWorker):
        async def run(self) -> None:
            pass

    @Module(providers=[CompletingWorker])
    class AppModule:
        pass

    async def scenario():
        app = WorkerAppFactory.create(AppModule)

        await app.run()
        await app.close()

        assert app.closed is True

    asyncio.run(scenario())


def test_cancelling_standalone_run_still_closes_the_application():
    @Injectable
    class LongRunningWorker(BackgroundWorker):
        def __init__(self):
            self.started = asyncio.Event()
            self.exited = False

        async def run(self) -> None:
            self.started.set()
            await self.stopping.wait()
            self.exited = True

    @Module(providers=[LongRunningWorker])
    class AppModule:
        pass

    async def scenario():
        app = WorkerAppFactory.create(AppModule, grace_timeout=0.1)
        worker = app.container.get(LongRunningWorker)
        run_task = asyncio.create_task(app.run())
        await asyncio.wait_for(worker.started.wait(), timeout=0.1)

        run_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await run_task

        assert app.closed is True
        assert worker.exited is True

    asyncio.run(scenario())


def test_run_workers_runs_a_completing_worker():
    calls = []

    @Injectable
    class CompletingWorker(BackgroundWorker):
        async def run(self) -> None:
            calls.append("ran")

    @Module(providers=[CompletingWorker])
    class AppModule:
        pass

    run_workers(AppModule, signals=[])

    assert calls == ["ran"]


def test_run_workers_rejects_use_inside_a_running_event_loop():
    @Module()
    class AppModule:
        pass

    async def scenario():
        with pytest.raises(RuntimeError, match="running event loop"):
            run_workers(AppModule)

    asyncio.run(scenario())
