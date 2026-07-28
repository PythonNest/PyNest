from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RestartPolicy(str, Enum):
    """Controls when a worker is restarted after ``run`` exits."""

    NONE = "none"
    ON_FAILURE = "on_failure"
    ALWAYS = "always"


class WorkerState(str, Enum):
    """Observable state of a managed background worker."""

    STARTING = "starting"
    RUNNING = "running"
    BACKING_OFF = "backing_off"
    STOPPING = "stopping"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class WorkerStatus:
    """Immutable snapshot returned by the worker host."""

    name: str
    state: WorkerState
    restarts: int = 0
    last_error: Optional[str] = None

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable status representation."""
        return {
            "name": self.name,
            "state": self.state.value,
            "restarts": self.restarts,
            "last_error": self.last_error,
        }


class BackgroundWorker(ABC):
    """
    Base class for dependency-injected, long-running application work.

    Worker subclasses do not need to call ``super().__init__()``. PyNest owns
    the stop event and recreates it each time the worker host starts.
    """

    name: str = ""
    restart: RestartPolicy = RestartPolicy.ON_FAILURE
    restart_backoff: float = 1.0
    restart_backoff_max: float = 30.0

    @abstractmethod
    async def run(self) -> None:
        """Run until the work completes or cooperative shutdown is requested."""
        raise NotImplementedError

    async def on_start(self) -> None:
        """Run once immediately before the worker is supervised."""

    async def on_stop(self) -> None:
        """Run once after cooperative shutdown has been requested."""

    @property
    def stopping(self) -> asyncio.Event:
        """Event set by PyNest when the worker should stop."""
        event = getattr(self, "_pynest_stopping_event", None)
        if event is None:
            event = asyncio.Event()
            self._pynest_stopping_event = event
        return event

    async def sleep(self, seconds: float) -> bool:
        """
        Sleep without delaying application shutdown.

        Returns ``True`` when the delay elapsed, or ``False`` when shutdown
        interrupted it.
        """
        if seconds < 0:
            raise ValueError("seconds must be greater than or equal to zero")
        if self.stopping.is_set():
            return False
        try:
            await asyncio.wait_for(self.stopping.wait(), timeout=seconds)
        except asyncio.TimeoutError:
            return True
        return False

    def _prepare_for_start(self) -> None:
        self._pynest_stopping_event = asyncio.Event()

    def _request_stop(self) -> None:
        self.stopping.set()


class IntervalWorker(BackgroundWorker):
    """
    A fixed-delay recurring worker.

    The interval starts after each ``execute`` call completes, so executions
    never overlap within one process.
    """

    interval: float = 60.0
    run_immediately: bool = False

    @abstractmethod
    async def execute(self) -> None:
        """Execute one occurrence of the recurring job."""
        raise NotImplementedError

    async def run(self) -> None:
        if self.interval <= 0:
            raise ValueError("interval must be greater than zero")

        if not self.run_immediately and not await self.sleep(self.interval):
            return

        while not self.stopping.is_set():
            await self.execute()
            if not await self.sleep(self.interval):
                return
