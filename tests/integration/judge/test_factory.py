from typing import Type, Optional

import pytest

from autoarena.api import api
from autoarena.judge.anthropic import AnthropicJudge
from autoarena.judge.base import Judge, AutomatedJudge
from autoarena.judge.cohere import CohereJudge
from autoarena.judge.factory import judge_factory, verify_judge_type_environment, JUDGE_TYPE_TO_CLASS
from autoarena.judge.gemini import GeminiJudge
from autoarena.judge.human import HumanJudge
from autoarena.judge.ollama import OllamaJudge
from autoarena.judge.openai import OpenAIJudge
from autoarena.judge.together import TogetherJudge
from tests.integration.judge.conftest import (
    unset_environment_variable,
    temporary_environment_variable,
    api_judge,
    TEST_JUDGE_MODEL_NAMES,
)


@pytest.mark.parametrize(
    "judge_type,expected_type,required_api_key",
    [
        (api.JudgeType.HUMAN, HumanJudge, None),
        (api.JudgeType.OLLAMA, OllamaJudge, None),
        (api.JudgeType.OPENAI, OpenAIJudge, "OPENAI_API_KEY"),
        (api.JudgeType.ANTHROPIC, AnthropicJudge, "ANTHROPIC_API_KEY"),
        (api.JudgeType.COHERE, CohereJudge, "COHERE_API_KEY"),
        (api.JudgeType.GEMINI, GeminiJudge, "GOOGLE_API_KEY"),
        (api.JudgeType.TOGETHER, TogetherJudge, "TOGETHER_API_KEY"),
        (api.JudgeType.CUSTOM, None, None),
    ],
)
def test__judge_factory(
    judge_type: api.JudgeType,
    expected_type: Optional[Type[Judge]],
    required_api_key: Optional[str],
) -> None:
    name = f"{expected_type.__name__}" if expected_type is not None else "missing type"
    model_name = TEST_JUDGE_MODEL_NAMES.get(judge_type, name)
    request = api_judge(judge_type, model_name)

    # verify that instantiation fails without API key when one is necessary
    if required_api_key is not None:
        with unset_environment_variable(required_api_key):
            with pytest.raises(Exception):
                judge_factory(request)

    # not implemented
    if expected_type is None:
        with pytest.raises(Exception):
            judge_factory(request)

    # verify correct type is instantiated
    else:
        if required_api_key is not None:
            with temporary_environment_variable(required_api_key, "dummy-api-key"):
                judge = judge_factory(request)
        else:
            judge = judge_factory(request)
        assert type(judge) is expected_type


@pytest.mark.parametrize(
    "judge_type",
    [
        # api.JudgeType.OLLAMA,  # ollama is set up in CI testing environment
        api.JudgeType.OPENAI,
        api.JudgeType.ANTHROPIC,
        api.JudgeType.COHERE,
        api.JudgeType.GEMINI,
        api.JudgeType.TOGETHER,
        api.JudgeType.BEDROCK,
    ],
)
def test__verify_judge_type_environment__fail(judge_type: api.JudgeType) -> None:
    judge_class = JUDGE_TYPE_TO_CLASS[judge_type]
    if judge_class is None:
        raise RuntimeError("implementation error")
    api_key_name = judge_class.API_KEY_NAME if issubclass(judge_class, AutomatedJudge) else None
    if api_key_name is not None:
        with unset_environment_variable(api_key_name):
            with pytest.raises(Exception):
                verify_judge_type_environment(judge_type)
    else:
        with pytest.raises(Exception):
            verify_judge_type_environment(judge_type)


@pytest.mark.parametrize(
    "judge_type",
    [
        api.JudgeType.HUMAN,
        api.JudgeType.OLLAMA,
        api.JudgeType.OPENAI,
        api.JudgeType.ANTHROPIC,
        api.JudgeType.COHERE,
        api.JudgeType.GEMINI,
        api.JudgeType.TOGETHER,
        # api.JudgeType.BEDROCK,  # TODO: set up Bedrock credentials
        api.JudgeType.CUSTOM,
    ],
)
def test__verify_judge_type_environment(judge_type: api.JudgeType) -> None:
    verify_judge_type_environment(judge_type)
