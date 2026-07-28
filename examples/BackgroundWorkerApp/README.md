# PyNest Background Worker Demo

This application gives visible, end-to-end proof of the background-worker
features:

- `QueueWorker` consumes jobs submitted by HTTP and calculates their squares.
- `HeartbeatWorker` runs a non-overlapping fixed-delay interval task.
- `ResilientWorker` deliberately fails on its first attempt, then demonstrates
  automatic restart and recovery.
- All eight workers receive the same singleton `DemoState` through dependency
  injection.
- `/demo/status` exposes live supervisor state, restart counts, the last error,
  job totals, heartbeat count, and lifecycle events.
- The terminal logs the first heartbeat and then every 50th heartbeat, roughly
  once per second with the demo interval.
- Closing the application requests cooperative worker shutdown before provider
  teardown.

## Run it

From the repository root:

```bash
uv sync --no-dev --group test
uv run python -m examples.BackgroundWorkerApp.main
```

The API listens on <http://localhost:8011>, and its Swagger UI is available at
<http://localhost:8011/docs>.

The resilient worker emits one expected error log at startup. That first
failure is intentional; the supervisor restarts it after 10 milliseconds.

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

## Submit background work

Create a job:

```bash
curl -s \
  -X POST http://localhost:8011/demo/jobs \
  -H "content-type: application/json" \
  -d '{"number": 7}'
```

The response is immediately returned with a generated ID:

```json
{
  "id": "GENERATED_JOB_ID",
  "number": 7,
  "status": "queued",
  "result": null
}
```

Use that ID to inspect the job after the queue worker processes it:

```bash
curl -s http://localhost:8011/demo/jobs/GENERATED_JOB_ID
```

The completed result proves the work happened outside the request handler:

```json
{
  "id": "GENERATED_JOB_ID",
  "number": 7,
  "status": "completed",
  "result": 49
}
```

## Inspect the workers

```bash
curl -s http://localhost:8011/demo/status
```

The response will show all eight workers running. The important recovery
evidence looks like this:

```json
{
  "name": "resilient",
  "state": "running",
  "restarts": 1,
  "last_error": "RuntimeError: intentional first-run failure"
}
```

The same response includes a growing `heartbeats` count, a
`resilient_worker_recovered` value of `true`, completed job totals, per-task
execution counters, and all eight worker `:start` lifecycle events.

Press Ctrl+C in the server terminal. PyNest requests cooperative shutdown and
runs each worker's `on_stop()` hook within the configured grace timeout.

## Run the automated proof

```bash
uv run pytest tests/test_examples/test_background_worker_app.py -q
```

The integration test starts the real ASGI lifespan, submits a job, waits for all
worker behaviors, and verifies graceful shutdown.
