from datetime import datetime
import os
from typing import Type

import pytest

from autostack.api import api
from autostack.judge.anthropic import AnthropicJudge
from autostack.judge.base import Judge, WrappingJudge
from autostack.judge.cohere import CohereJudge
from autostack.judge.factory import judge_factory
from autostack.judge.gemini import GeminiJudge
from autostack.judge.human import HumanJudge
from autostack.judge.ollama import OllamaJudge
from autostack.judge.openai import OpenAIJudge
from autostack.judge.utils import ABShufflingJudge, CleaningJudge, RetryingJudge


@pytest.mark.parametrize(
    "judge_type,expected_type,required_api_key",
    [
        (api.JudgeType.HUMAN, HumanJudge, None),
        (api.JudgeType.OLLAMA, OllamaJudge, None),
        (api.JudgeType.OPENAI, OpenAIJudge, "OPENAI_API_KEY"),
        (api.JudgeType.ANTHROPIC, AnthropicJudge, "ANTHROPIC_API_KEY"),
        (api.JudgeType.COHERE, CohereJudge, "COHERE_API_KEY"),
        (api.JudgeType.GEMINI, GeminiJudge, "GOOGLE_API_KEY"),
        (api.JudgeType.CUSTOM, None, None),
    ],
)
def test__factory(judge_type: api.JudgeType, expected_type: Type[Judge] | None, required_api_key: str | None) -> None:
    if required_api_key is not None:
        os.environ[required_api_key] = "dummy-api-key"
    name = f"{expected_type.__name__}" if expected_type is not None else "missing type"
    request = api.Judge(
        id=-1,
        judge_type=judge_type,
        created=datetime.utcnow(),
        name=name,
        model_name=name,
        system_prompt="example system prompt",
        description="example_description",
        enabled=True,
        votes=0,
    )
    if expected_type is None:
        with pytest.raises(Exception):
            judge_factory(request)
    else:
        assert type(judge_factory(request)) is expected_type


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
            judge = judge.judge
