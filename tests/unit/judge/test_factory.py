from datetime import datetime
from typing import Type

import pytest

from autoarena.api import api
from autoarena.judge.base import WrappingJudge
from autoarena.judge.factory import judge_factory
from autoarena.judge.human import HumanJudge
from autoarena.judge.utils import ABShufflingJudge, CleaningJudge, RetryingJudge


def test__judge_factory__human() -> None:
    request = api.Judge(
        id=0,
        judge_type=api.JudgeType.HUMAN,
        created=datetime.utcnow(),
        name="Human",
        model_name=None,
        system_prompt=None,
        description="Example description",
        enabled=True,
        votes=0,
    )
    judge = judge_factory(request)
    assert type(judge) is HumanJudge
    assert judge.judge_type is api.JudgeType.HUMAN
    assert judge.name == "Human"
    assert judge.model_name is None
    assert judge.system_prompt is None
    assert judge.description is not None
    with pytest.raises(NotImplementedError):
        judge.judge(api.HeadToHead(prompt="p", result_a_id=100, result_b_id=200, response_a="a", response_b="b"))


def test__judge_factory__custom() -> None:
    request = api.Judge(
        id=0,
        judge_type=api.JudgeType.CUSTOM,
        created=datetime.utcnow(),
        name="CustomJudge",
        model_name="abc",
        system_prompt="Always say 'A'",
        description="Example description",
        enabled=True,
        votes=0,
    )
    with pytest.raises(NotImplementedError):
        judge_factory(request)


@pytest.mark.parametrize("wrappers", [([]), ([ABShufflingJudge]), (ABShufflingJudge, CleaningJudge, RetryingJudge)])
def test__judge_factory__wrappers(wrappers: list[Type[WrappingJudge]]) -> None:
    request = api.Judge(
        id=-1,
        judge_type=api.JudgeType.HUMAN,
        created=datetime.utcnow(),
        name="human",
        model_name=None,
        system_prompt=None,
        description="example_description",
        enabled=True,
        votes=0,
    )
    judge = judge_factory(request, wrappers=wrappers)
    if len(wrappers) == 0:
        assert type(judge) is HumanJudge
    else:
        for wrapper_type in wrappers[::-1]:
            assert type(judge) is wrapper_type
            judge = judge.wrapped
