import threading
import unittest

from app.core.errors import AppError
from app.infrastructure import jobs
from tests.helpers import client  # noqa: F401  (sets up env + DB)


class JobLockTest(unittest.TestCase):
    def test_second_job_of_same_kind_is_409(self):
        gate = threading.Event()
        first = jobs.start("lock-test", lambda: (gate.wait(5), {"ok": True})[1])
        with self.assertRaises(AppError) as ctx:
            jobs.start("lock-test", lambda: {"ok": True})
        self.assertEqual(ctx.exception.status, 409)
        gate.set()
        for _ in range(100):
            if jobs.get(first)["status"] != "running":
                break
            threading.Event().wait(0.05)
        self.assertEqual(jobs.get(first)["status"], "done")

    def test_failed_job_hides_internals(self):
        def boom():
            raise RuntimeError("secret path /etc/x")
        job_id = jobs.start("fail-test", boom, background=False)
        j = jobs.get(job_id)
        self.assertEqual(j["status"], "failed")
        self.assertNotIn("secret", j["error"])


if __name__ == "__main__":
    unittest.main()
