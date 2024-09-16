import os
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

from autoarena.api import api
from autoarena.service.judge import JudgeService

TEST_JUDGE_MODEL_NAMES: dict[api.JudgeType, str] = {
    api.JudgeType.OLLAMA: "qwen2:0.5b",
    api.JudgeType.OPENAI: "gpt-4o-mini",
    api.JudgeType.ANTHROPIC: "claude-3-haiku-20240307",
    api.JudgeType.COHERE: "command-r",
    api.JudgeType.GEMINI: "gemini-1.5-flash",
    api.JudgeType.TOGETHER: "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    api.JudgeType.BEDROCK: "meta.llama3-1-8b-instruct-v1:0",
    api.JudgeType.HUGGINGFACE: "meta-llama/Meta-Llama-3-8B-Instruct",
}


@contextmanager
def unset_environment_variable(key: str) -> Iterator[None]:
    prev = os.environ.get(key, None)
    if prev is not None:
        del os.environ[key]
    try:
        yield
    finally:
        if prev is not None:
            os.environ[key] = prev


@contextmanager
def temporary_environment_variable(key: str, value: str) -> Iterator[None]:
    prev = os.environ.get(key, None)
    os.environ[key] = value
    try:
        yield
    finally:
        if prev is not None:
            os.environ[key] = prev


def api_judge(judge_type: api.JudgeType, model_name: str) -> api.Judge:
    return api.Judge(
        id=0,
        judge_type=judge_type,
        created=datetime.utcnow(),
        name=f"{judge_type.name}",
        model_name=model_name,
        system_prompt=JudgeService.get_default_system_prompt(),
        description="Example description",
        enabled=True,
        n_votes=0,
    )
