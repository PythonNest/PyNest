# Background Worker Demo App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a runnable PyNest HTTP application whose API and integration test visibly prove queued work, interval work, dependency injection, failure recovery, worker status reporting, and graceful shutdown.

**Architecture:** A singleton `DemoState` provider owns an in-memory `asyncio.Queue`, job records, heartbeat count, recovery state, and lifecycle events. Three injected workers consume the queue, run an interval heartbeat, and intentionally fail once before recovering; a controller exposes job submission and a combined demo/worker-status view. A real `TestClient` lifespan test drives the application end to end.

**Tech Stack:** Python 3.10+, PyNest, FastAPI, Pydantic, asyncio, pytest

---

## File Structure

- `examples/BackgroundWorkerApp/src/demo_service.py`: in-memory demo state and job queue.
- `examples/BackgroundWorkerApp/src/demo_workers.py`: queue, interval, and recovery workers.
- `examples/BackgroundWorkerApp/src/app_controller.py`: HTTP endpoints for submitting work and observing proof.
- `examples/BackgroundWorkerApp/src/app_module.py`: PyNest module, app factory, and worker-host status binding.
- `examples/BackgroundWorkerApp/main.py`: Uvicorn entry point.
- `examples/BackgroundWorkerApp/README.md`: runbook and expected evidence.
- `tests/test_examples/test_background_worker_app.py`: lifespan-level proof that all worker behaviors succeed.

### Task 1: Write the end-to-end proof

**Files:**
- Create: `tests/test_examples/__init__.py`
- Create: `tests/test_examples/test_background_worker_app.py`

- [ ] **Step 1: Write the failing integration test**

```python
import time
from typing import Callable

from fastapi.testclient import TestClient

from examples.BackgroundWorkerApp.src.app_module import create_app
from examples.BackgroundWorkerApp.src.demo_service import DemoState


def wait_for(assertion: Callable[[], None], timeout: float = 2.0) -> None:
    deadline = time.monotonic() + timeout
    while True:
        try:
            assertion()
            return
        except AssertionError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.01)


def test_demo_proves_background_workers_run_recover_and_stop() -> None:
    app = create_app()
    state = app.container.get(DemoState)

    with TestClient(app.get_server()) as client:
        response = client.post("/demo/jobs", json={"number": 7})
        assert response.status_code == 202
        job_id = response.json()["id"]

        def assert_background_results() -> None:
            job = client.get(f"/demo/jobs/{job_id}").json()
            dashboard = client.get("/demo/status").json()
            workers = {item["name"]: item for item in dashboard["workers"]}

            assert job["status"] == "completed"
            assert job["result"] == 49
            assert dashboard["demo"]["heartbeats"] >= 2
            assert dashboard["demo"]["resilient_worker_recovered"] is True
            assert workers["queue-processor"]["state"] == "running"
            assert workers["heartbeat"]["state"] == "running"
            assert workers["resilient"]["state"] == "running"
            assert workers["resilient"]["restarts"] == 1
            assert workers["resilient"]["last_error"] == (
                "RuntimeError: intentional first-run failure"
            )

        wait_for(assert_background_results)

    assert {item["state"] for item in app.get_worker_host().status()} == {"stopped"}
    assert {
        "queue-processor:stop",
        "heartbeat:stop",
        "resilient:stop",
    }.issubset(state.lifecycle_events)
```

- [ ] **Step 2: Run the test and verify the app does not exist yet**

Run: `uv run pytest tests/test_examples/test_background_worker_app.py -q`

Expected: collection fails with `ModuleNotFoundError` for `examples.BackgroundWorkerApp`.

### Task 2: Implement injected state and worker behaviors

**Files:**
- Create: `examples/BackgroundWorkerApp/__init__.py`
- Create: `examples/BackgroundWorkerApp/src/__init__.py`
- Create: `examples/BackgroundWorkerApp/src/demo_service.py`
- Create: `examples/BackgroundWorkerApp/src/demo_workers.py`

- [ ] **Step 1: Implement the singleton queue and observable state**

`DemoState` will:

- create jobs with UUID identifiers and a `queued` status;
- expose a coroutine that waits briefly for either a queued job or shutdown;
- mark jobs `processing` and then `completed` with the square of their input;
- count interval heartbeats;
- record whether the resilient worker recovered;
- return JSON-ready job and summary dictionaries;
- retain worker start/stop lifecycle event names.

- [ ] **Step 2: Implement the queue worker**

```python
@Injectable
class QueueWorker(BackgroundWorker):
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
```

- [ ] **Step 3: Implement the interval worker**

```python
@Injectable
class HeartbeatWorker(IntervalWorker):
    name = "heartbeat"
    interval = 0.02
    run_immediately = True

    def __init__(self, state: DemoState):
        self.state = state

    async def on_start(self) -> None:
        self.state.record_lifecycle(f"{self.name}:start")

    async def execute(self) -> None:
        self.state.record_heartbeat()

    async def on_stop(self) -> None:
        self.state.record_lifecycle(f"{self.name}:stop")
```

- [ ] **Step 4: Implement restart-on-failure proof**

```python
@Injectable
class ResilientWorker(BackgroundWorker):
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
```

### Task 3: Wire the runnable HTTP app

**Files:**
- Create: `examples/BackgroundWorkerApp/src/app_controller.py`
- Create: `examples/BackgroundWorkerApp/src/app_module.py`
- Create: `examples/BackgroundWorkerApp/main.py`

- [ ] **Step 1: Add the controller**

Create:

- `POST /demo/jobs` accepting a Pydantic model with integer `number`, returning HTTP 202 and the queued record;
- `GET /demo/jobs/{job_id}` returning the current job record or FastAPI HTTP 404;
- `GET /demo/status` returning `{"workers": ..., "demo": ...}`.

- [ ] **Step 2: Bind the app-local worker host**

Register `DemoState`, `WorkerStatusService`, and all three workers as singleton module providers. `create_app()` will call `PyNestFactory.create()`, bind that app's `WorkerHost` to its `WorkerStatusService`, and return the `PyNestApp`. Export module-level `app` and `http_server` values for Uvicorn.

- [ ] **Step 3: Add the executable entry point**

```python
import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "examples.BackgroundWorkerApp.src.app_module:http_server",
        host="0.0.0.0",
        port=8011,
        reload=True,
    )
```

### Task 4: Document and verify the demonstration

**Files:**
- Create: `examples/BackgroundWorkerApp/README.md`

- [ ] **Step 1: Document the proof flow**

Include the exact `uv run python -m examples.BackgroundWorkerApp.main` command, `curl` commands for job submission, job inspection, and worker status, the expected squared result, the expected resilient-worker restart metadata, and the expected clean shutdown behavior after Ctrl+C.

- [ ] **Step 2: Format and run the focused test**

Run: `uv run black --config /dev/null --check examples/BackgroundWorkerApp tests/test_examples/test_background_worker_app.py`

Expected: exit code 0.

Run: `uv run pytest tests/test_examples/test_background_worker_app.py -q`

Expected: `1 passed`.

- [ ] **Step 3: Run the full suite**

Run: `uv run pytest tests -q`

Expected: all tests pass.

- [ ] **Step 4: Inspect the final diff**

Run: `git diff --check && git status --short`

Expected: no whitespace errors; only the planned demo, integration test, and plan files are changed.
