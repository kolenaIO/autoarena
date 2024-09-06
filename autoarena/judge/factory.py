from typing import Optional

from autoarena.api import api
from autoarena.judge.anthropic import AnthropicJudge
from autoarena.judge.base import Judge, WrappingJudge, AutomatedJudge
from autoarena.judge.bedrock import BedrockJudge
from autoarena.judge.cohere import CohereJudge
from autoarena.judge.custom import create_custom_judge, CustomJudge
from autoarena.judge.gemini import GeminiJudge
from autoarena.judge.human import HumanJudge
from autoarena.judge.ollama import OllamaJudge
from autoarena.judge.openai import OpenAIJudge
from autoarena.judge.together import TogetherJudge

JUDGE_TYPE_TO_CLASS: dict[api.JudgeType, type[Judge]] = {
    api.JudgeType.HUMAN: HumanJudge,
    api.JudgeType.OLLAMA: OllamaJudge,
    api.JudgeType.OPENAI: OpenAIJudge,
    api.JudgeType.ANTHROPIC: AnthropicJudge,
    api.JudgeType.COHERE: CohereJudge,
    api.JudgeType.GEMINI: GeminiJudge,
    api.JudgeType.TOGETHER: TogetherJudge,
    api.JudgeType.BEDROCK: BedrockJudge,
    api.JudgeType.CUSTOM: CustomJudge,  # type: ignore
}


def judge_factory(judge: api.Judge, wrappers: Optional[list[type[WrappingJudge]]] = None) -> Judge:
    def judge_factory_inner(j: api.Judge):
        if j.judge_type is api.JudgeType.CUSTOM:
            return create_custom_judge(judge)
        judge_class = JUDGE_TYPE_TO_CLASS.get(j.judge_type, None)
        if judge_class is None:
            raise ValueError(f"unrecognized judge type: {j.judge_type}")
        if judge_class is HumanJudge:
            return HumanJudge()
        if not issubclass(judge_class, AutomatedJudge) or j.model_name is None or j.system_prompt is None:
            raise ValueError(f"misconfigured judge: {j}")
        return judge_class(j.model_name, j.system_prompt)

    constructed_judge = judge_factory_inner(judge)
    if wrappers is not None and len(wrappers) > 0:
        for wrapper in wrappers:
            constructed_judge = wrapper(constructed_judge)
    return constructed_judge


def verify_judge_type_environment(judge_type: api.JudgeType) -> None:
    judge_class = JUDGE_TYPE_TO_CLASS.get(judge_type, None)
    if judge_class is None:
        raise ValueError(f"unrecognized judge type: {judge_type}")
    judge_class.verify_environment()


def verify_judge_environment(judge: api.Judge) -> None:
    verify_judge_type_environment(judge.judge_type)
    judge_factory(judge)  # verify that this judge can be instantiated
