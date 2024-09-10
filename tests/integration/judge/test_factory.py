from typing import Type

import pytest

from autoarena.api import api
from autoarena.judge.anthropic import AnthropicJudge
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.bedrock import BedrockJudge
from autoarena.judge.cohere import CohereJudge
from autoarena.judge.factory import judge_factory, verify_judge_type_environment, JUDGE_TYPE_TO_CLASS
from autoarena.judge.gemini import GeminiJudge
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
    "judge_type,expected_type",
    [
        (api.JudgeType.OPENAI, OpenAIJudge),
        (api.JudgeType.ANTHROPIC, AnthropicJudge),
        (api.JudgeType.COHERE, CohereJudge),
        (api.JudgeType.GEMINI, GeminiJudge),
        (api.JudgeType.TOGETHER, TogetherJudge),
    ],
)
def test__judge_factory__automated__with_key(judge_type: api.JudgeType, expected_type: Type[AutomatedJudge]) -> None:
    name = f"{expected_type.__name__}" if expected_type is not None else "missing type"
    model_name = TEST_JUDGE_MODEL_NAMES.get(judge_type, name)
    request = api_judge(judge_type, model_name)
    required_api_key = expected_type.API_KEY_NAME
    assert required_api_key is not None

    # verify that instantiation fails without API key
    with unset_environment_variable(required_api_key):
        with pytest.raises(Exception):
            judge_factory(request)

    # verify that instantiation succeeds with API key, even if it's not correct
    with temporary_environment_variable(required_api_key, "dummy-api-key"):
        judge = judge_factory(request)
    assert type(judge) is expected_type
    assert judge.judge_type is judge_type
    assert judge.model_name == model_name
    assert judge.description is not None


@pytest.mark.parametrize(
    "judge_type,expected_type",
    [
        (api.JudgeType.OLLAMA, OllamaJudge),
        (api.JudgeType.BEDROCK, BedrockJudge),
    ],
)
def test__judge_factory__automated__no_key(judge_type: api.JudgeType, expected_type: Type[AutomatedJudge]) -> None:
    model_name = TEST_JUDGE_MODEL_NAMES[judge_type]
    request = api_judge(judge_type, model_name)
    judge = judge_factory(request)
    assert type(judge) is expected_type
    assert judge.judge_type is judge_type
    assert judge.model_name == model_name
    assert judge.description is not None


@pytest.mark.parametrize(
    "judge_type",
    [
        # api.JudgeType.OLLAMA,  # ollama is set up in CI testing environment
        api.JudgeType.OPENAI,
        api.JudgeType.ANTHROPIC,
        api.JudgeType.COHERE,
        api.JudgeType.GEMINI,
        api.JudgeType.TOGETHER,
        # api.JudgeType.BEDROCK,  # credentials for bedrock access are set up in CI testing environment
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
        api.JudgeType.BEDROCK,
        api.JudgeType.CUSTOM,
    ],
)
def test__verify_judge_type_environment(judge_type: api.JudgeType) -> None:
    verify_judge_type_environment(judge_type)
