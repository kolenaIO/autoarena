import pytest

from autoarena.api import api
from autoarena.judge.factory import judge_factory
from autoarena.judge.wrapper import cleaning_wrapper
from tests.integration.judge.conftest import api_judge, TEST_JUDGE_MODEL_NAMES

H2H = api.HeadToHead(prompt="What is 2+2?", response_a_id=1, response_b_id=2, response_a="4", response_b="100 million")


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
    judge_instance = judge_factory(api_judge(judge_type, model_name), wrappers=[cleaning_wrapper])
    assert judge_instance.judge(H2H) == "A"
    assert judge_instance.n_calls == 1
    assert judge_instance.total_input_tokens > 0
    assert judge_instance.total_output_tokens > 0
