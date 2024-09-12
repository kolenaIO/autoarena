import time

import pytest

from autoarena.api import api
from autoarena.judge.utils import rate_limit

DUMMY_H2H = api.HeadToHead(prompt="test prompt", response_a_id=-1, response_b_id=-2, response_a="a", response_b="b")


def test__rate_limit() -> None:
    call_times: list[float] = []

    @rate_limit(n_calls=2, n_seconds=1.05, n_call_buffer=1, backoff_seconds=0.2)
    def caller() -> None:
        nonlocal call_times
        call_times.append(time.time())

    caller()
    caller()
    first_call, second_call = call_times
    assert second_call - first_call > 1


def test__rate_limit__failed() -> None:
    call_times: list[float] = []

    @rate_limit(n_calls=2, n_seconds=2, n_call_buffer=1, max_wait_seconds=1, backoff_seconds=0.2)
    def caller() -> None:
        nonlocal call_times
        call_times.append(time.time())

    caller()
    with pytest.raises(RuntimeError):
        caller()
