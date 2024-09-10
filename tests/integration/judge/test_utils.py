import pytest

from autoarena.judge.utils import FixingJudge
from tests.unit.judge.test_utils import DUMMY_H2H
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
    ],
)
def test__fixing_judge(raw: str, expected: str) -> None:
    test_judge = DummyJudge([raw])
    assert FixingJudge(test_judge).judge(DUMMY_H2H) == expected
