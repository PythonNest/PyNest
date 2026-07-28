import asyncio

import pytest

from nest.common.background_worker import (
    BackgroundWorker,
    RestartPolicy,
    WorkerState,
)
from nest.core import Injectable, Module
from nest.core.pynest_container import PyNestContainer
from nest.core.worker_host import WorkerHost


def test_container_discovers_each_worker_provider_once():
    @Injectable
    class TestWorker(BackgroundWorker):
        async def run(self) -> None:
            pass

    @Module(providers=[TestWorker])
    class WorkerModule:
        pass

    @Module(imports=[WorkerModule], providers=[TestWorker])
    class AppModule:
        pass

    container = PyNestContainer()
    container.add_module(AppModule)
    container.build()

    assert container.get_instances_of(BackgroundWorker) == [container.get(TestWorker)]


def test_get_instances_of_requires_a_built_container():
    container = PyNestContainer()

    with pytest.raises(RuntimeError, match="build"):
        container.get_instances_of(BackgroundWorker)


def test_host_starts_and_cooperatively_stops_a_worker():
    class CooperativeWorker(BackgroundWorker):
        name = "cooperative"

        def __init__(self):
            self.started = asyncio.Event()
            self.on_start_calls = 0
            self.on_stop_calls = 0
            self.exited = False

        async def on_start(self) -> None:
            self.on_start_calls += 1

        async def run(self) -> None:
            self.started.set()
            await self.stopping.wait()
            self.exited = True

        async def on_stop(self) -> None:
            self.on_stop_calls += 1

    async def scenario():
        worker = CooperativeWorker()
        host = WorkerHost([worker], grace_timeout=0.1)

        await host.start()
        await asyncio.wait_for(worker.started.wait(), timeout=0.1)
        assert host.status() == [
            {
                "name": "cooperative",
                "state": "running",
                "restarts": 0,
                "last_error": None,
            }
        ]

        await host.stop()
        await host.stop()

        assert worker.on_start_calls == 1
        assert worker.on_stop_calls == 1
        assert worker.exited is True
        assert host.get_status()[0].state is WorkerState.STOPPED

    asyncio.run(scenario())


def test_host_restarts_a_failed_worker_with_backoff():
    class FailsOnceWorker(BackgroundWorker):
        restart_backoff = 0

        def __init__(self):
            self.attempts = 0
            self.succeeded = asyncio.Event()

        async def run(self) -> None:
            self.attempts += 1
            if self.attempts == 1:
                raise RuntimeError("temporary failure")
            self.succeeded.set()
            await self.stopping.wait()

    async def scenario():
        worker = FailsOnceWorker()
        host = WorkerHost([worker], grace_timeout=0.1)

        await host.start()
        await asyncio.wait_for(worker.succeeded.wait(), timeout=0.1)

        status = host.get_status()[0]
        assert worker.attempts == 2
        assert status.restarts == 1
        assert status.last_error == "RuntimeError: temporary failure"
        assert status.state is WorkerState.RUNNING

        await host.stop()

    asyncio.run(scenario())


def test_none_policy_leaves_a_crashed_worker_failed():
    class FailingWorker(BackgroundWorker):
        restart = RestartPolicy.NONE

        async def run(self) -> None:
            raise LookupError("permanent failure")

    async def scenario():
        host = WorkerHost([FailingWorker()])

        await host.start()
        await asyncio.wait_for(host.wait(), timeout=0.1)

        assert host.status() == [
            {
                "name": "FailingWorker",
                "state": "failed",
                "restarts": 0,
                "last_error": "LookupError: permanent failure",
            }
        ]

        await host.stop()

    asyncio.run(scenario())


def test_always_policy_restarts_a_normally_completed_worker():
    class RepeatWorker(BackgroundWorker):
        restart = RestartPolicy.ALWAYS
        restart_backoff = 0

        def __init__(self):
            self.calls = 0
            self.restarted = asyncio.Event()

        async def run(self) -> None:
            self.calls += 1
            if self.calls == 2:
                self.restarted.set()
                await self.stopping.wait()

    async def scenario():
        worker = RepeatWorker()
        host = WorkerHost([worker], grace_timeout=0.1)

        await host.start()
        await asyncio.wait_for(worker.restarted.wait(), timeout=0.1)

        assert host.get_status()[0].restarts == 1
        await host.stop()

    asyncio.run(scenario())


def test_host_cancels_a_worker_after_the_grace_timeout():
    class StubbornWorker(BackgroundWorker):
        def __init__(self):
            self.started = asyncio.Event()
            self.never = asyncio.Event()
            self.cancelled = False

        async def run(self) -> None:
            self.started.set()
            try:
                await self.never.wait()
            except asyncio.CancelledError:
                self.cancelled = True
                raise

    async def scenario():
        worker = StubbornWorker()
        host = WorkerHost([worker], grace_timeout=0.01)

        await host.start()
        await asyncio.wait_for(worker.started.wait(), timeout=0.1)
        await host.stop()

        assert worker.cancelled is True
        assert host.get_status()[0].state is WorkerState.STOPPED

    asyncio.run(scenario())


def test_stop_timeout_also_bounds_slow_on_stop_hooks():
    class SlowStopWorker(BackgroundWorker):
        def __init__(self):
            self.started = asyncio.Event()
            self.hook_cancelled = False

        async def run(self) -> None:
            self.started.set()
            await self.stopping.wait()

        async def on_stop(self) -> None:
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                self.hook_cancelled = True
                raise

    async def scenario():
        worker = SlowStopWorker()
        host = WorkerHost([worker], grace_timeout=0.01)

        await host.start()
        await asyncio.wait_for(worker.started.wait(), timeout=0.1)
        await host.stop()

        assert worker.hook_cancelled is True

    asyncio.run(scenario())


def test_stop_waits_for_start_hook_before_calling_stop_hook():
    class SlowStartWorker(BackgroundWorker):
        def __init__(self):
            self.starting = asyncio.Event()
            self.release_start = asyncio.Event()
            self.events = []

        async def on_start(self) -> None:
            self.events.append("start:begin")
            self.starting.set()
            await self.release_start.wait()
            self.events.append("start:end")

        async def run(self) -> None:
            self.events.append("run")

        async def on_stop(self) -> None:
            self.events.append("stop")

    async def scenario():
        worker = SlowStartWorker()
        host = WorkerHost([worker], grace_timeout=0.1)
        await host.start()
        await asyncio.wait_for(worker.starting.wait(), timeout=0.1)

        stop_task = asyncio.create_task(host.stop())
        await asyncio.sleep(0)
        worker.release_start.set()
        await asyncio.wait_for(stop_task, timeout=0.1)

        assert worker.events == ["start:begin", "start:end", "stop"]

    asyncio.run(scenario())


def test_duplicate_worker_names_are_rejected():
    class FirstWorker(BackgroundWorker):
        name = "duplicate"

        async def run(self) -> None:
            pass

    class SecondWorker(BackgroundWorker):
        name = "duplicate"

        async def run(self) -> None:
            pass

    with pytest.raises(ValueError, match="Duplicate background worker name"):
        WorkerHost([FirstWorker(), SecondWorker()])


def test_blank_worker_name_falls_back_to_the_class_name():
    class BlankNameWorker(BackgroundWorker):
        name = "   "

        async def run(self) -> None:
            pass

    assert WorkerHost([BlankNameWorker()]).status()[0]["name"] == "BlankNameWorker"


def test_host_rejects_values_that_are_not_workers():
    with pytest.raises(TypeError, match="BackgroundWorker"):
        WorkerHost([object()])


@pytest.mark.parametrize(
    ("attribute", "value", "message"),
    [
        ("restart", "sometimes", "restart policy"),
        ("restart_backoff", -1, "restart_backoff"),
        ("restart_backoff_max", -1, "restart_backoff_max"),
    ],
)
def test_invalid_worker_configuration_is_rejected(attribute, value, message):
    class InvalidWorker(BackgroundWorker):
        async def run(self) -> None:
            pass

    setattr(InvalidWorker, attribute, value)

    with pytest.raises(ValueError, match=message):
        WorkerHost([InvalidWorker()])


def test_negative_grace_timeout_is_rejected():
    with pytest.raises(ValueError, match="grace_timeout"):
        WorkerHost([], grace_timeout=-1)
