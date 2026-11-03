import threading
import time

import pytest

from app.core.errors import AppError
from app.infrastructure import jobs


def test_second_run_of_same_kind_is_409():
    gate = threading.Event()
    first = jobs.start("lock-test", lambda: (gate.wait(5), {"ok": True})[1])
    with pytest.raises(AppError) as e:
        jobs.start("lock-test", lambda: {"ok": True})
    assert e.value.status == 409
    gate.set()
    for _ in range(50):
        if jobs.get(first).status != "running":
            break
        time.sleep(0.1)
    assert jobs.get(first).status == "done"
    assert jobs.start("lock-test", lambda: {"ok": True}, background=False)


def test_failure_does_not_leak_internals():
    def boom():
        raise RuntimeError("secret internal path /etc/x")
    jid = jobs.start("fail-test", boom, background=False)
    j = jobs.get(jid)
    assert j.status == "failed" and "secret" not in (j.error or "")
