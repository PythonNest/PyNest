import asyncio

import pytest

from nest.common.background_worker import (
    BackgroundWorker,
    IntervalWorker,
    RestartPolicy,
    WorkerState,
    WorkerStatus,
)


class ProbeWorker(BackgroundWorker):
    async def run(self) -> None:
        pass


def test_background_worker_has_safe_restart_defaults():
    worker = ProbeWorker()

    assert worker.name == ""
    assert worker.restart is RestartPolicy.ON_FAILURE
    assert worker.restart_backoff == 1.0
    assert worker.restart_backoff_max == 30.0
    assert worker.stopping.is_set() is False


def test_worker_does_not_require_subclasses_to_call_super_init():
    class WorkerWithDependencies(BackgroundWorker):
        def __init__(self, dependency):
            self.dependency = dependency

        async def run(self) -> None:
            pass

    worker = WorkerWithDependencies(object())

    assert worker.stopping.is_set() is False


def test_sleep_returns_true_after_the_delay_elapses():
    async def scenario():
        worker = ProbeWorker()

        assert await worker.sleep(0) is True

    asyncio.run(scenario())


def test_sleep_returns_false_when_stop_is_requested():
    async def scenario():
        worker = ProbeWorker()
        task = asyncio.create_task(worker.sleep(10))
        await asyncio.sleep(0)

        worker.stopping.set()

        assert await asyncio.wait_for(task, timeout=0.1) is False

    asyncio.run(scenario())


def test_sleep_rejects_negative_delays():
    async def scenario():
        worker = ProbeWorker()

        with pytest.raises(ValueError, match="greater than or equal to zero"):
            await worker.sleep(-0.1)

    asyncio.run(scenario())


def test_prepare_for_start_replaces_a_previous_stop_event():
    worker = ProbeWorker()
    old_event = worker.stopping
    old_event.set()

    worker._prepare_for_start()

    assert worker.stopping is not old_event
    assert worker.stopping.is_set() is False


def test_interval_worker_runs_immediately_and_never_overlaps_executions():
    class ProbeIntervalWorker(IntervalWorker):
        interval = 0.001
        run_immediately = True

        def __init__(self):
            self.calls = 0
            self.in_flight = 0
            self.max_in_flight = 0

        async def execute(self) -> None:
            self.calls += 1
            self.in_flight += 1
            self.max_in_flight = max(self.max_in_flight, self.in_flight)
            await asyncio.sleep(0)
            self.in_flight -= 1
            if self.calls == 2:
                self.stopping.set()

    async def scenario():
        worker = ProbeIntervalWorker()
        await worker.run()

        assert worker.calls == 2
        assert worker.max_in_flight == 1

    asyncio.run(scenario())


def test_interval_worker_waits_before_first_execution_by_default():
    class DelayedWorker(IntervalWorker):
        interval = 10

        def __init__(self):
            self.calls = 0

        async def execute(self) -> None:
            self.calls += 1

    async def scenario():
        worker = DelayedWorker()
        task = asyncio.create_task(worker.run())
        await asyncio.sleep(0)

        assert worker.calls == 0

        worker.stopping.set()
        await asyncio.wait_for(task, timeout=0.1)
        assert worker.calls == 0

    asyncio.run(scenario())


def test_interval_worker_rejects_a_negative_interval():
    class InvalidIntervalWorker(IntervalWorker):
        interval = -1

        async def execute(self) -> None:
            pass

    async def scenario():
        with pytest.raises(ValueError, match="greater than zero"):
            await InvalidIntervalWorker().run()

    asyncio.run(scenario())


def test_worker_status_is_immutable_and_json_ready():
    status = WorkerStatus(
        name="email",
        state=WorkerState.BACKING_OFF,
        restarts=2,
        last_error="connection lost",
    )

    assert status.as_dict() == {
        "name": "email",
        "state": "backing_off",
        "restarts": 2,
        "last_error": "connection lost",
    }
    with pytest.raises(AttributeError):
        status.restarts = 3
