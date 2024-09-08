import pytest

from autoarena.api import api
from autoarena.judge.factory import judge_factory
from autoarena.judge.utils import CleaningJudge
from tests.integration.judge.conftest import api_judge, TEST_JUDGE_MODEL_NAMES

H2H = api.HeadToHead(prompt="What is 2+2?", result_a_id=1, result_b_id=2, response_a="4", response_b="100 million")


@pytest.mark.parametrize(
    "judge_type",
    [
        api.JudgeType.OPENAI,
        api.JudgeType.ANTHROPIC,
        api.JudgeType.COHERE,
        api.JudgeType.GEMINI,
        api.JudgeType.TOGETHER,
    ],
)
def test__judge__proprietary(judge_type: api.JudgeType) -> None:
    model_name = TEST_JUDGE_MODEL_NAMES[judge_type]
    judge_instance = judge_factory(api_judge(judge_type, model_name), wrappers=[CleaningJudge])
    assert judge_instance.judge(H2H) == "A"


@pytest.mark.skip(reason="Not implemented -- auth is a little more difficult than an API key here")
def test__judge__bedrock() -> None:
    raise NotImplementedError


def test__judge__ollama() -> None:
    model_name = TEST_JUDGE_MODEL_NAMES[api.JudgeType.OLLAMA]
    judge_instance = judge_factory(api_judge(api.JudgeType.OLLAMA, model_name))
    assert judge_instance.judge(H2H) == "A"
