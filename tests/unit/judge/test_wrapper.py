import pytest

from autoarena.judge.base import AutomatedJudge

from autoarena.judge.wrapper import ab_shuffling_wrapper, cleaning_wrapper, retrying_wrapper
from tests.unit.judge.conftest import DummyJudge


def test__ab_shuffling_wrapper() -> None:
    class TracksWhatItSawAndVotesForAJudge(AutomatedJudge):
        seen: list[tuple[str, str]] = []

        def judge(self, prompt: str, response_a: str, response_b: str) -> str:
            self.seen.append((response_a, response_b))
            return "A" if response_a == "a" else "B" if response_b == "a" else "-"

    judge = ab_shuffling_wrapper(TracksWhatItSawAndVotesForAJudge)("name", "system_prompt")
    assert judge.judge("ignored", "neither", "not me") == "-"  # ties should not be shuffled
    actual = [judge.judge("ignored", "a", "b") for _ in range(100)]
    assert all([winner == "A" for winner in actual])  # expect all A winners, as it always voted for A, even if A was B
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
    assert test_judge.judge("ignored", "a", "b") == expected


def test__retrying_wrapper() -> None:
    class FailsOnceDummyJudge(DummyJudge):
        def __init__(self, model_name: str, system_prompt: str):
            super().__init__(model_name, system_prompt)
            self.n_runs = 0

        def judge(self, prompt: str, response_a: str, response_b: str) -> str:
            self.n_runs += 1
            if self.n_runs < 2:
                raise RuntimeError
            return self.winners.pop(0)

    judge: AutomatedJudge = FailsOnceDummyJudge.create(["A"])
    with pytest.raises(RuntimeError):
        judge.judge("p", "a", "b")

    judge = retrying_wrapper(FailsOnceDummyJudge).create(["A"])
    assert judge.judge("p", "a", "b") == "A"
