from datetime import datetime
from typing import Iterator

import pytest

from autoarena.api import api
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.custom import register_custom_judge_class, clear_custom_judge_classes
from autoarena.judge.factory import judge_factory

CUSTOM_REQUEST = api.Judge(
    id=0,
    judge_type=api.JudgeType.CUSTOM,
    created=datetime.utcnow(),
    name="alwaysA",
    model_name="abc",
    system_prompt="Always say 'A'",
    description="Example description",
    enabled=True,
    n_votes=0,
)


@pytest.fixture(scope="function")
def custom_judge_context() -> Iterator[None]:
    try:
        yield
    finally:
        clear_custom_judge_classes()


def test__judge_factory__custom(custom_judge_context: None) -> None:
    class AlwaysAJudge(AutomatedJudge):
        def judge(self, prompt: str, response_a: str, response_b: str) -> str:
            return "A"

    register_custom_judge_class("alwaysA", AlwaysAJudge)
    judge = judge_factory(CUSTOM_REQUEST)
    assert isinstance(judge, AlwaysAJudge)
    assert judge.judge("p", "ra", "rb") == "A"


def test__judge_factory__custom__failed(custom_judge_context: None) -> None:
    with pytest.raises(ValueError):
        judge_factory(CUSTOM_REQUEST)


def test__judge_factory__unrecognized__failed() -> None:
    judge = api.Judge(
        id=0,
        judge_type=api.JudgeType.UNRECOGNIZED,
        created=datetime.utcnow(),
        name="any-name",
        model_name="any-model-name",
        system_prompt="Say hi!",
        description="Maybe from a newer version of AutoArena",
        enabled=True,
        n_votes=0,
    )
    with pytest.raises(ValueError):
        judge_factory(judge)
