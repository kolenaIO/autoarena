import numpy as np
import pytest

from autoarena.api import api
from autoarena.judge.base import AutomatedJudge

from autoarena.judge.wrapper import ab_shuffling_wrapper, cleaning_wrapper, retrying_wrapper
from tests.unit.judge.conftest import DummyJudge
from tests.unit.judge.test_utils import DUMMY_H2H


def test__ab_shuffling_wrapper() -> None:
    class TracksWhatItSawDummyJudge(DummyJudge):
        seen: list[tuple[str, str]] = []

        def judge(self, h2h: api.HeadToHead) -> str:
            self.seen.append((h2h.response_a, h2h.response_b))
            return self.winners.pop(0)

    expected = ["A"] * 100
    judge = ab_shuffling_wrapper(TracksWhatItSawDummyJudge).create([*expected])
    actual = [judge.judge(DUMMY_H2H) for _ in range(len(expected))]
    assert len(actual) == len(expected)
    assert np.array_equal((np.array(actual) == "-"), (np.array(expected) == "-"))  # ties should not be shuffled
    assert any([winner == "A" for winner in actual])  # expect both A and B winners, despite only returning A
    assert any([winner == "B" for winner in actual])
    assert any([a == "a" for a, b in judge.seen])  # expect that it saw response A and response B shuffled
    assert any([a == "b" for a, b in judge.seen])
    assert any([b == "a" for a, b in judge.seen])
    assert any([b == "b" for a, b in judge.seen])


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
def test__cleaning_wrapper(raw: str, expected: str) -> None:
    test_judge = cleaning_wrapper(DummyJudge).create([raw])
    assert test_judge.judge(DUMMY_H2H) == expected


def test__retrying_wrapper() -> None:
    class FailsOnceDummyJudge(DummyJudge):
        def __init__(self, model_name: str, system_prompt: str):
            super().__init__(model_name, system_prompt)
            self.n_runs = 0

        def judge(self, h2h: api.HeadToHead) -> str:
            self.n_runs += 1
            if self.n_runs < 2:
                raise RuntimeError
            return self.winners.pop(0)

    judge: AutomatedJudge = FailsOnceDummyJudge.create(["A"])
    with pytest.raises(RuntimeError):
        judge.judge(DUMMY_H2H)

    judge = retrying_wrapper(FailsOnceDummyJudge).create(["A"])
    assert judge.judge(DUMMY_H2H) == "A"
