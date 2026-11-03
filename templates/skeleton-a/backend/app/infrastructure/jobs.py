"""Long-running work: one running job per kind (second request -> 409), status kept in DB."""
import json
import logging
import threading
from collections.abc import Callable
from datetime import datetime, timezone

from app.core.errors import AppError
from app.infrastructure.db import SessionLocal
from app.infrastructure.models import Job

log = logging.getLogger("app")
_lock = threading.Lock()


def start(kind: str, work: Callable[[], object], background: bool = True) -> int:
    """Create a job row and run `work` (must return JSON-serializable data). Raises 409 if same kind is running."""
    with _lock:
        with SessionLocal() as db:
            running = db.query(Job).filter(Job.kind == kind, Job.status == "running").first()
            if running:
                raise AppError(409, "job_running", "같은 작업이 이미 실행 중입니다.", {"job_id": running.id})
            job = Job(kind=kind, status="running")
            db.add(job)
            db.commit()
            job_id = job.id
    if background:
        threading.Thread(target=_run, args=(job_id, work), daemon=True).start()
    else:
        _run(job_id, work)
    return job_id


def _run(job_id: int, work: Callable[[], object]) -> None:
    status, result, error = "done", None, None
    try:
        result = json.dumps(work(), ensure_ascii=False)
    except AppError as e:
        status, error = "failed", e.message
    except Exception:  # keep internals out of the API
        log.exception("job %s failed", job_id)
        status, error = "failed", "작업 중 오류가 발생했습니다."
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        job.status, job.result, job.error = status, result, error
        job.finished_at = datetime.now(timezone.utc)
        db.commit()


def get(job_id: int) -> Job:
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        if not job:
            raise AppError(404, "not_found", "작업을 찾을 수 없습니다.")
        return job
