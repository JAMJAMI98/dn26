import time

from app.infrastructure import jobs
from app.presentation.deps import login_required, require_role
from app.presentation.http import Response


def register(router, settings):
    @router.route("GET", "/api/jobs/{job_id:int}")
    @login_required
    def get_job(req):
        return Response(200, jobs.get(req.params["job_id"]))

    # Example of a long task. Replace with the task's own work (e.g. "generate"), keep the pattern.
    @router.route("POST", "/api/jobs/example")
    @require_role("admin")
    def start_example(req):
        seconds = min(float(req.q("seconds", "1") or 1), 10)
        job_id = jobs.start("example", lambda: (time.sleep(seconds), {"ok": True})[1])
        return Response(202, jobs.get(job_id))
