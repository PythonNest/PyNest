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

    assert all(worker.state is state for worker in app.get_worker_host().workers)

    with TestClient(app.get_server()) as client:
        response = client.post("/demo/jobs", json={"number": 7})

        assert response.status_code == 202
        job_id = response.json()["id"]

        def assert_background_results() -> None:
            job_response = client.get(f"/demo/jobs/{job_id}")
            dashboard_response = client.get("/demo/status")

            assert job_response.status_code == 200
            assert dashboard_response.status_code == 200

            job = job_response.json()
            dashboard = dashboard_response.json()
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

        wait_for(assert_background_results)

    assert {item["state"] for item in app.get_worker_host().status()} == {"stopped"}
    assert {
        "queue-processor:stop",
        "heartbeat:stop",
        "resilient:stop",
    }.issubset(state.lifecycle_events)
    assert {
        "cache-refresh:stop",
        "metrics-flush:stop",
        "session-cleanup:stop",
        "report-generation:stop",
        "data-sync:stop",
    }.issubset(state.lifecycle_events)
