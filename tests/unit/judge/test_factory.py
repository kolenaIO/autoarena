import datetime
import os
from typing import Type

import pytest

from autostack.api import api
from autostack.judge.anthropic import AnthropicJudge
from autostack.judge.base import Judge
from autostack.judge.cohere import CohereJudge
from autostack.judge.factory import judge_factory
from autostack.judge.gemini import GeminiJudge
from autostack.judge.human import HumanJudge
from autostack.judge.ollama import OllamaJudge
from autostack.judge.openai import OpenAIJudge


@pytest.mark.parametrize(
    "judge_type,expected_type,required_api_key",
    [
        (api.JudgeType.HUMAN, HumanJudge, None),
        (api.JudgeType.OLLAMA, OllamaJudge, None),
        (api.JudgeType.OPENAI, OpenAIJudge, "OPENAI_API_KEY"),
        (api.JudgeType.ANTHROPIC, AnthropicJudge, None),
        (api.JudgeType.COHERE, CohereJudge, "COHERE_API_KEY"),
        (api.JudgeType.GEMINI, GeminiJudge, None),
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
        created=datetime.datetime.now(datetime.UTC),
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
