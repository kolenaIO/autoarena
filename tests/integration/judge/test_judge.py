from datetime import datetime

import pytest

from autoarena.api import api
from autoarena.judge.factory import judge_factory
from autoarena.judge.utils import CleaningJudge
from autoarena.service.judge import JudgeService


@pytest.mark.parametrize(
    "judge_type,model_name",
    [
        (api.JudgeType.OPENAI, "gpt-4o-mini"),
        (api.JudgeType.ANTHROPIC, "claude-3-haiku-20240307"),
        (api.JudgeType.COHERE, "command-r"),
        (api.JudgeType.GEMINI, "gemini-1.5-flash"),
        (api.JudgeType.TOGETHER, "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"),
    ],
)
def test__judge__proprietary(judge_type: api.JudgeType, model_name: str) -> None:
    judge_api = api.Judge(
        id=0,
        judge_type=judge_type,
        created=datetime.utcnow(),
        name=f"{judge_type.name}",
        model_name=model_name,
        system_prompt=JudgeService.get_default_system_prompt(),
        description="Example description",
        enabled=True,
        votes=0,
    )
    judge_instance = judge_factory(judge_api, wrappers=[CleaningJudge])
    h2h = api.HeadToHead(prompt="What is 2+2?", result_a_id=1, result_b_id=2, response_a="4", response_b="100 million")
    winner = judge_instance.judge(h2h)
    assert winner == "A"  # TODO: will all judges pass this?


@pytest.mark.skip(reason="Not implemented -- auth is a little more difficult than an API key here")
def test__judge__bedrock() -> None:
    raise NotImplementedError


@pytest.mark.skip(reason="Not implemented -- requires Ollama service running in environment")
def test__judge__ollama() -> None:
    raise NotImplementedError
