import time

import numpy as np
import pytest

from autoarena.api import api
from autoarena.api.api import JudgeType
from autoarena.judge.base import Judge
from autoarena.judge.utils import CleaningJudge, RetryingJudge, FixingJudge, ABShufflingJudge, rate_limit

# this is more or less a constant as it is baked into the @rate_limit decorators applied to proprietary judges
DEFAULT_BATCH_SIZE = 8


class DummyJudge(Judge):
    def __init__(self, winners: list[str]):
        self._winners = winners

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.CUSTOM

    @property
    def name(self) -> str:
        return "test"

    @property
    def model_name(self) -> str | None:
        return None

    @property
    def system_prompt(self) -> str | None:
        return None

    @property
    def description(self) -> str:
        return "judge for testing"

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        return self._winners


DUMMY_H2H = api.HeadToHead(prompt="test prompt", result_a_id=-1, result_b_id=-2, response_a="a", response_b="b")


def test__ab_shuffling_judge() -> None:
    expected = ["A", "B", "-"]
    judge = ABShufflingJudge(DummyJudge(expected))
    actual = judge.judge_batch([DUMMY_H2H] * 3)
    assert len(actual) == len(expected)
    assert np.array_equal((np.array(actual) == "-"), (np.array(expected) == "-"))  # ties should not be shuffled
    # TODO: assertion that the shuffling+unshuffling is actually taking place as advertised


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("A", "A"),
        ("B", "B"),
        ("-", "-"),
        ("foobar", "-"),
        ("'A'", "A"),
        ("A.", "A"),
        ('"B."', "B"),
        ("The better response is B.", "-"),  # doesn't fix these
        ("\n\n\tA.\n\n", "A"),
        ("\n\n\t'-'\n\n", "-"),
        ("**A.**", "A"),
    ],
)
def test__cleaning_judge(raw: str, expected: str) -> None:
    test_judge = DummyJudge([raw])
    assert CleaningJudge(test_judge).judge_batch([DUMMY_H2H]) == [expected]


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("A", "A"),
        ("B", "B"),
        ("-", "-"),
        ("A is better.", "A"),
        ("Response B is better, because it does a better job than A.", "B"),
        ("Neither A nor B are that good.", "-"),
    ],
)
def test__fixing_judge(raw: str, expected: str) -> None:
    test_judge = DummyJudge([raw])
    assert FixingJudge(test_judge).judge_batch([DUMMY_H2H]) == [expected]


def test__retrying_judge() -> None:
    class FailsOnceDummyJudge(DummyJudge):
        def __init__(self, winners: list[str]):
            super().__init__(winners)
            self.n_runs = 0

        def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
            self.n_runs += 1
            if self.n_runs < 2:
                raise RuntimeError
            return self._winners

    expected = ["A"]
    judge: Judge = FailsOnceDummyJudge(expected)
    with pytest.raises(RuntimeError):
        judge.judge_batch([DUMMY_H2H])

    judge = RetryingJudge(FailsOnceDummyJudge(expected))
    assert judge.judge_batch([DUMMY_H2H]) == expected


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
