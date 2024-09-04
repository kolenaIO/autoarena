import pytest

from autostack.api import api
from autostack.api.api import JudgeType
from autostack.judge.base import Judge
from autostack.judge.utils import CleaningJudge, RetryingJudge, FixingJudge, ABShufflingJudge


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
    assert judge.judge_batch([DUMMY_H2H] * 3) == expected


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
