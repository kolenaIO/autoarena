from typing import Type

from autostack.api import api
from autostack.judge.anthropic import AnthropicJudge
from autostack.judge.base import Judge, WrappingJudge
from autostack.judge.cohere import CohereJudge
from autostack.judge.gemini import GeminiJudge
from autostack.judge.human import HumanJudge
from autostack.judge.ollama import OllamaJudge
from autostack.judge.openai import OpenAIJudge


def judge_factory(judge: api.Judge, wrappers: list[Type[WrappingJudge]] | None = None) -> Judge:
    def judge_factory_inner(j: api.Judge):
        if j.judge_type is api.JudgeType.HUMAN:
            return HumanJudge()
        if j.judge_type is api.JudgeType.CUSTOM:
            raise NotImplementedError(f"judge type '{j.judge_type}' not yet implemented")
        if j.model_name is None or j.system_prompt is None:
            raise ValueError(f"misconfigured judge: {j}")
        if j.judge_type is api.JudgeType.OLLAMA:
            return OllamaJudge(j.model_name, j.system_prompt)
        if j.judge_type is api.JudgeType.OPENAI:
            return OpenAIJudge(j.model_name, j.system_prompt)
        if j.judge_type is api.JudgeType.ANTHROPIC:
            return AnthropicJudge(j.model_name, j.system_prompt)
        if j.judge_type is api.JudgeType.COHERE:
            return CohereJudge(j.model_name, j.system_prompt)
        if j.judge_type is api.JudgeType.GEMINI:
            return GeminiJudge(j.model_name, j.system_prompt)
        raise ValueError(f"unrecognized judge type: {j}")

    constructed_judge = judge_factory_inner(judge)
    if wrappers is not None and len(wrappers) > 0:
        for wrapper in wrappers:
            constructed_judge = wrapper(constructed_judge)
    return constructed_judge
