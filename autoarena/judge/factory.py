from typing import Type, Optional

from autoarena.api import api
from autoarena.judge.anthropic import AnthropicJudge
from autoarena.judge.base import WrappingJudge, AutomatedJudge
from autoarena.judge.bedrock import BedrockJudge
from autoarena.judge.cohere import CohereJudge
from autoarena.judge.gemini import GeminiJudge
from autoarena.judge.ollama import OllamaJudge
from autoarena.judge.openai import OpenAIJudge
from autoarena.judge.together import TogetherJudge

AUTOMATED_JUDGE_TYPE_TO_CLASS: dict[api.JudgeType, Optional[Type[AutomatedJudge]]] = {
    api.JudgeType.OLLAMA: OllamaJudge,
    api.JudgeType.OPENAI: OpenAIJudge,
    api.JudgeType.ANTHROPIC: AnthropicJudge,
    api.JudgeType.COHERE: CohereJudge,
    api.JudgeType.GEMINI: GeminiJudge,
    api.JudgeType.TOGETHER: TogetherJudge,
    api.JudgeType.BEDROCK: BedrockJudge,
    api.JudgeType.CUSTOM: None,
}


def judge_factory(judge: api.Judge, wrappers: Optional[list[Type[WrappingJudge]]] = None) -> AutomatedJudge:
    def judge_factory_inner(j: api.Judge) -> AutomatedJudge:
        if j.judge_type is api.JudgeType.CUSTOM:
            raise NotImplementedError(f"judge type '{j.judge_type}' not yet implemented")
        if j.judge_type is api.JudgeType.HUMAN:
            raise ValueError("automated judge factory cannot instantiate human judge")
        judge_class = AUTOMATED_JUDGE_TYPE_TO_CLASS.get(j.judge_type, None)
        if judge_class is None:
            raise ValueError(f"unrecognized judge type: {j.judge_type}")
        if not issubclass(judge_class, AutomatedJudge) or j.model_name is None or j.system_prompt is None:
            raise ValueError(f"misconfigured judge: {j}")
        return judge_class(j.model_name, j.system_prompt)

    constructed_judge = judge_factory_inner(judge)
    if wrappers is not None and len(wrappers) > 0:
        for wrapper in wrappers:
            constructed_judge = wrapper(constructed_judge)
    return constructed_judge


def verify_judge_type_environment(judge_type: api.JudgeType) -> None:
    judge_class = AUTOMATED_JUDGE_TYPE_TO_CLASS.get(judge_type, None)
    if judge_class is not None:
        judge_class.verify_environment()
