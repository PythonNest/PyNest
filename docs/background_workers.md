# Background workers

PyNest can run dependency-injected work alongside an HTTP application or in a
dedicated process without an HTTP server. The framework starts worker tasks on
the runtime event loop, supervises failures, and stops them before application
shutdown hooks dispose their dependencies.

## Long-running workers

Create an injectable provider that extends `BackgroundWorker`:

```python
import asyncio

from nest.core import BackgroundWorker, Injectable, Module


@Injectable
class EmailWorker(BackgroundWorker):
    name = "email"

    def __init__(self, queue: EmailQueue):
        self.queue = queue

    async def run(self) -> None:
        while not self.stopping.is_set():
            try:
                message = await asyncio.wait_for(
                    self.queue.receive(),
                    timeout=1,
                )
            except asyncio.TimeoutError:
                continue

            await self.queue.deliver(message)


@Module(providers=[EmailQueue, EmailWorker])
class AppModule:
    pass
```

Register the worker in `providers` like any other service. Constructor
dependencies are resolved by the PyNest container, and the host retains the
resolved instance for the application lifespan. Singleton scope is recommended
for worker providers.

Do not start tasks from a worker constructor or lifecycle hook. PyNest calls
`run()` from FastAPI's lifespan event loop, which keeps asyncio resources on the
same loop that owns the application.

### Cooperative shutdown

`self.stopping` is set when shutdown begins. Long-running loops should inspect
it, and idle delays should use `self.sleep()`:

```python
async def run(self) -> None:
    while not self.stopping.is_set():
        await self.flush_batch()
        if not await self.sleep(5):
            return
```

`sleep(seconds)` returns `True` when the delay elapsed and `False` when shutdown
interrupted it. PyNest first requests cooperative shutdown and calls
`on_stop()`. If the worker is still running after the grace timeout, its task is
cancelled and drained.

`on_start()` and `on_stop()` are optional. They may be synchronous or
asynchronous, but `run()` must be asynchronous.

## Recurring interval jobs

`IntervalWorker` is a fixed-delay scheduler built on the same supervisor:

```python
from nest.core import Injectable, IntervalWorker


@Injectable
class CleanupWorker(IntervalWorker):
    name = "expired-session-cleanup"
    interval = 300
    run_immediately = True

    def __init__(self, sessions: SessionRepository):
        self.sessions = sessions

    async def execute(self) -> None:
        await self.sessions.delete_expired()
```

The delay starts after `execute()` finishes, so occurrences never overlap
within one process. `interval` must be greater than zero. By default, the first
occurrence waits for one interval; set `run_immediately = True` to run once at
startup.

Calendar and cron scheduling are intentionally not implemented in core.
Production cron scheduling needs explicit policies for time zones, daylight
saving changes, missed executions, persistence, and distributed locking. Use a
dedicated scheduler in a worker provider when those semantics are required.

## Restart policies

Workers default to restarting after an exception:

```python
from nest.core import RestartPolicy


class QueueWorker(BackgroundWorker):
    restart = RestartPolicy.ON_FAILURE
    restart_backoff = 1
    restart_backoff_max = 30
```

The available policies are:

| Policy | Exception | Normal return |
| --- | --- | --- |
| `RestartPolicy.NONE` | Stop as failed | Stop as completed |
| `RestartPolicy.ON_FAILURE` | Restart | Stop as completed |
| `RestartPolicy.ALWAYS` | Restart | Restart |

Restarts use capped exponential backoff. Cancellation and application shutdown
never trigger a restart.

An unhandled `IntervalWorker.execute()` exception follows the same policy as
any other worker failure.

## HTTP applications

No extra startup code is needed:

```python
from nest.core import PyNestFactory

app = PyNestFactory.create(
    AppModule,
    worker_grace_timeout=15,
    title="API and workers",
)
```

Workers start when the ASGI lifespan starts, not when
`PyNestFactory.create()` returns. They stop before PyNest runs provider and
module shutdown hooks.

Inspect worker state for a health or administration endpoint:

```python
worker_status = app.get_worker_host().status()
```

The result is JSON-ready:

```json
[
  {
    "name": "email",
    "state": "running",
    "restarts": 1,
    "last_error": "ConnectionError: broker unavailable"
  }
]
```

States are `starting`, `running`, `backing_off`, `stopping`, `stopped`,
`completed`, and `failed`.

## Standalone worker processes

Use `run_workers()` for a process that does not serve HTTP:

```python
from nest.core import run_workers

from src.app_module import AppModule


if __name__ == "__main__":
    run_workers(AppModule, grace_timeout=15)
```

The standalone runner:

1. Builds the dependency container.
2. Runs bootstrap lifecycle hooks on its event loop.
3. Starts all registered workers on that same loop.
4. Handles `SIGTERM` and `SIGINT`.
5. Stops workers before running shutdown hooks.

For an existing async entrypoint, use the application object instead:

```python
from nest.core import WorkerAppFactory


async def main() -> None:
    app = WorkerAppFactory.create(AppModule)
    await app.run()
```

Do not call `run_workers()` from a running event loop; it raises a clear error
instead of nesting `asyncio.run()`.

## Deployment behavior

Every application process runs its own instance of every registered worker. If
Uvicorn starts four processes, an HTTP-integrated interval worker runs four
times.

Use one of these patterns when work must run only once:

- Deploy `run_workers()` as a separate single-replica service.
- Partition queue consumption so the broker coordinates consumers.
- Protect scheduled work with a distributed lock.
- Use a scheduler that persists and coordinates jobs across processes.

Worker status is local to one process and resets when that process restarts.
