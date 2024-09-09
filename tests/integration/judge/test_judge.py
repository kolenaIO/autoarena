import pytest

from autoarena.api import api
from autoarena.judge.factory import judge_factory
from autoarena.judge.utils import CleaningJudge
from tests.integration.judge.conftest import api_judge, TEST_JUDGE_MODEL_NAMES


@pytest.mark.parametrize(
    "judge_type",
    [
        api.JudgeType.OLLAMA,
        api.JudgeType.OPENAI,
        api.JudgeType.ANTHROPIC,
        api.JudgeType.COHERE,
        api.JudgeType.GEMINI,
        api.JudgeType.TOGETHER,
        api.JudgeType.BEDROCK,
    ],
)
def test__judge__automated(judge_type: api.JudgeType) -> None:
    model_name = TEST_JUDGE_MODEL_NAMES[judge_type]
    judge_instance = judge_factory(api_judge(judge_type, model_name), wrappers=[CleaningJudge])
    h2h = api.HeadToHead(
        result_a=api.Result(id=1, prompt="What is 2+2?", response="4"),
        result_b=api.Result(id=2, prompt="What is 2+2?", response="100 million"),
    )
    assert judge_instance.judge(h2h) == "A"
