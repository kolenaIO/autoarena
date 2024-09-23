import pytest

from autoarena.judge.wrapper import fixing_wrapper
from tests.unit.judge.conftest import DummyJudge


# this involves downloading and running a classification model and can be quite slow -- consider it an integration test
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("A", "A"),
        ("B", "B"),
        ("-", "-"),
        ("A is better.", "A"),
        ("Response B is better, because it does a better job than A.", "B"),
        ("Neither A nor B are that good.", "-"),
        ("", "-"),  # empty responses are properly marked as ties
    ],
)
def test__fixing_wrapper(raw: str, expected: str) -> None:
    test_judge = fixing_wrapper(DummyJudge)("dummy", "dummy", "description")
    test_judge.winners = [raw]
    assert test_judge.judge("p", "a", "b") == expected
