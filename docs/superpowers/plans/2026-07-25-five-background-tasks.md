# Five Background Tasks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the background-worker demo with five independently supervised, observable periodic tasks.

**Architecture:** A reusable `ObservableIntervalWorker` will provide dependency injection, lifecycle recording, execution counters, and visible logging. Five small subclasses will define distinct task names and intervals, while `DemoState` and `/demo/status` expose their execution counts for the live demo and integration test.

**Tech Stack:** Python 3.10+, PyNest `IntervalWorker`, asyncio, FastAPI, pytest

---

## File Structure

- `examples/BackgroundWorkerApp/src/additional_workers.py`: reusable interval-task behavior and five registered worker classes.
- `examples/BackgroundWorkerApp/src/demo_service.py`: counters for each new background task.
- `examples/BackgroundWorkerApp/src/app_module.py`: registration of the five worker providers.
- `tests/test_examples/test_background_worker_app.py`: running, execution, dependency-injection, and shutdown proof for all five.
- `examples/BackgroundWorkerApp/README.md`: live behavior and status-field documentation.

### Task 1: Extend the failing integration proof

**Files:**
- Modify: `tests/test_examples/test_background_worker_app.py`

- [ ] **Step 1: Assert all five workers execute and remain running**

```python
additional_tasks = {
    "cache-refresh": "cache_refresh",
    "metrics-flush": "metrics_flush",
    "session-cleanup": "session_cleanup",
    "report-generation": "report_generation",
    "data-sync": "data_sync",
}

for worker_name, task_name in additional_tasks.items():
    assert workers[worker_name]["state"] == "running"
    assert dashboard["demo"]["background_tasks"][task_name] >= 1
```

- [ ] **Step 2: Assert all five workers stop cooperatively**

```python
assert {
    "cache-refresh:stop",
    "metrics-flush:stop",
    "session-cleanup:stop",
    "report-generation:stop",
    "data-sync:stop",
}.issubset(state.lifecycle_events)
```

- [ ] **Step 3: Run the focused test and verify it fails**

Run: `uv run pytest tests/test_examples/test_background_worker_app.py -q`

Expected: FAIL because the five worker names and `background_tasks` summary do not exist yet.

### Task 2: Add observable task state

**Files:**
- Modify: `examples/BackgroundWorkerApp/src/demo_service.py`

- [ ] **Step 1: Initialize the task counters**

```python
self._background_task_runs: Counter[str] = Counter()
```

- [ ] **Step 2: Record and expose task executions**

```python
def record_background_task(self, task_name: str) -> int:
    self._background_task_runs[task_name] += 1
    return self._background_task_runs[task_name]
```

Add this entry to `summary()`:

```python
"background_tasks": dict(self._background_task_runs),
```

### Task 3: Implement five interval workers

**Files:**
- Create: `examples/BackgroundWorkerApp/src/additional_workers.py`

- [ ] **Step 1: Add the shared observable worker**

```python
import logging

from nest.core import Injectable, IntervalWorker

from .demo_service import DemoState

logger = logging.getLogger("uvicorn.error")


@Injectable
class ObservableIntervalWorker(IntervalWorker):
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
```

- [ ] **Step 2: Define the five independently configured providers**

```python
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
```

### Task 4: Register and document the tasks

**Files:**
- Modify: `examples/BackgroundWorkerApp/src/app_module.py`
- Modify: `examples/BackgroundWorkerApp/README.md`

- [ ] **Step 1: Register all five providers**

Add this import:

```python
from .additional_workers import (
    CacheRefreshWorker,
    DataSyncWorker,
    MetricsFlushWorker,
    ReportGenerationWorker,
    SessionCleanupWorker,
)
```

Use this provider list:

```python
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
```

- [ ] **Step 2: Document the observable behaviors**

Add this runbook section:

```markdown
## Additional periodic tasks

Five more independently supervised interval workers run alongside the original
demo:

- `cache-refresh` every 2 seconds
- `metrics-flush` every 3 seconds
- `session-cleanup` every 4 seconds
- `report-generation` every 5 seconds
- `data-sync` every 6 seconds

Each runs immediately at startup. Executions appear as `Background task ...
completed` terminal logs and as counters under `demo.background_tasks` in
`/demo/status`.
```

- [ ] **Step 3: Run focused verification**

Run: `uv run black --config /dev/null --check examples/BackgroundWorkerApp tests/test_examples/test_background_worker_app.py`

Expected: exit code 0.

Run: `uv run pytest tests/test_examples/test_background_worker_app.py -q`

Expected: `1 passed`.

- [ ] **Step 4: Run full and live verification**

Run: `uv run pytest tests -q`

Expected: all tests pass.

Observe the already-running Uvicorn session after reload.

Expected: all five `Background task ... completed (run=1)` messages appear and `/demo/status` reports eight running workers.
