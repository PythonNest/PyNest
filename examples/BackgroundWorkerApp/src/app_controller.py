from fastapi import HTTPException
from pydantic import BaseModel

from nest.core import Controller, Get, Post

from .demo_service import DemoState, WorkerStatusService


class SubmitJobRequest(BaseModel):
    number: int


@Controller("/demo", tag="background-workers")
class AppController:
    def __init__(self, state: DemoState, worker_status: WorkerStatusService):
        self.state = state
        self.worker_status = worker_status

    @Post("/jobs", status_code=202)
    async def submit_job(self, request: SubmitJobRequest) -> dict[str, object]:
        return self.state.submit(request.number)

    @Get("/jobs/{job_id}")
    async def get_job(self, job_id: str) -> dict[str, object]:
        job = self.state.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return job

    @Get("/status")
    async def get_status(self) -> dict[str, object]:
        return {
            "workers": self.worker_status.status(),
            "demo": self.state.summary(),
        }
