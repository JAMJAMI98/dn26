import time

from fastapi import APIRouter, Depends

from app.infrastructure import jobs
from app.presentation.deps import current_user, require_role
from app.presentation.schemas import JobOut

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _out(job) -> JobOut:
    return JobOut(id=job.id, kind=job.kind, status=job.status, result=job.result, error=job.error)


@router.get("/{job_id}", response_model=JobOut, dependencies=[Depends(current_user)])
def get_job(job_id: int):
    return _out(jobs.get(job_id))


# Example of a long task. Replace with the task's own work (e.g. "generate"), keep the pattern.
@router.post("/example", response_model=JobOut, status_code=202, dependencies=[Depends(require_role("admin"))])
def start_example(seconds: float = 1.0):
    job_id = jobs.start("example", lambda: (time.sleep(min(seconds, 10)), {"ok": True})[1])
    return _out(jobs.get(job_id))
