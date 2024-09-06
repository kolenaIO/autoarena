from datetime import datetime
from typing import Type

import pytest

from autoarena.api import api
from autoarena.judge.base import WrappingJudge
from autoarena.judge.factory import judge_factory
from autoarena.judge.human import HumanJudge
from autoarena.judge.utils import ABShufflingJudge, CleaningJudge, RetryingJudge


@pytest.mark.parametrize("wrappers", [([]), ([ABShufflingJudge]), (ABShufflingJudge, CleaningJudge, RetryingJudge)])
def test__factory_wrappers(wrappers: list[Type[WrappingJudge]]) -> None:
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
