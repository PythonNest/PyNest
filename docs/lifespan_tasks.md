# Lifespan tasks in PyNest

Long-running coroutines should use PyNest's
[background worker](background_workers.md) support. Awaiting an infinite
coroutine directly from a FastAPI startup handler prevents startup from
completing and does not provide supervised failure or bounded shutdown.

For a recurring task, extend `IntervalWorker`:

```python
from datetime import datetime

from nest.core import Injectable, IntervalWorker, Module, PyNestFactory


@Injectable
class ClockWorker(IntervalWorker):
    interval = 3600
    run_immediately = True

    async def execute(self) -> None:
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"Current time: {current_time}")


@Module(providers=[ClockWorker])
class AppModule:
    pass


app = PyNestFactory.create(AppModule)
```

PyNest starts the worker inside the ASGI lifespan and stops it when the
application shuts down. See [Background workers](background_workers.md) for
long-running consumers, restart policies, status inspection, and standalone
worker processes.
