import os
from datetime import datetime
from typing import Type

import pytest

from autoarena.api import api
from autoarena.judge.anthropic import AnthropicJudge
from autoarena.judge.base import Judge
from autoarena.judge.cohere import CohereJudge
from autoarena.judge.factory import judge_factory
from autoarena.judge.gemini import GeminiJudge
from autoarena.judge.human import HumanJudge
from autoarena.judge.openai import OpenAIJudge
from autoarena.judge.together import TogetherJudge


@pytest.mark.parametrize(
    "judge_type,expected_type,required_api_key",
    [
        (api.JudgeType.HUMAN, HumanJudge, None),
        # TODO: reenable as integration test (requires communication with Ollama service to instantiate)
        # (api.JudgeType.OLLAMA, OllamaJudge, None),
        (api.JudgeType.OPENAI, OpenAIJudge, "OPENAI_API_KEY"),
        (api.JudgeType.ANTHROPIC, AnthropicJudge, "ANTHROPIC_API_KEY"),
        (api.JudgeType.COHERE, CohereJudge, "COHERE_API_KEY"),
        (api.JudgeType.GEMINI, GeminiJudge, "GOOGLE_API_KEY"),
        (api.JudgeType.TOGETHER, TogetherJudge, "TOGETHER_API_KEY"),
        (api.JudgeType.CUSTOM, None, None),
    ],
)
def test__factory(judge_type: api.JudgeType, expected_type: Type[Judge] | None, required_api_key: str | None) -> None:
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

    # verify that instantiation fails without API key when one is necessary
    if required_api_key is not None:
        if os.environ.get(required_api_key, None) is not None:
            del os.environ[required_api_key]
        with pytest.raises(Exception):
            judge_factory(request)
        os.environ[required_api_key] = "dummy-api-key"

    # verify that instantiation succeeds with API key
    if expected_type is None:
        with pytest.raises(Exception):
            judge_factory(request)
    else:
        assert type(judge_factory(request)) is expected_type
