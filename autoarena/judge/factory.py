from typing import Optional, Sequence

from autoarena.api import api
from autoarena.judge.anthropic import AnthropicJudge
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.bedrock import BedrockJudge
from autoarena.judge.cohere import CohereJudge
from autoarena.judge.custom import get_custom_judge_class
from autoarena.judge.gemini import GeminiJudge
from autoarena.judge.ollama import OllamaJudge
from autoarena.judge.openai import OpenAIJudge
from autoarena.judge.together import TogetherJudge
from autoarena.judge.wrapper import JudgeWrapper

AUTOMATED_JUDGE_TYPE_TO_CLASS: dict[api.JudgeType, type[AutomatedJudge]] = {
    api.JudgeType.OLLAMA: OllamaJudge,
    api.JudgeType.OPENAI: OpenAIJudge,
    api.JudgeType.ANTHROPIC: AnthropicJudge,
    api.JudgeType.COHERE: CohereJudge,
    api.JudgeType.GEMINI: GeminiJudge,
    api.JudgeType.TOGETHER: TogetherJudge,
    api.JudgeType.BEDROCK: BedrockJudge,
}


def judge_factory(judge: api.Judge, wrappers: Optional[Sequence[JudgeWrapper]] = None) -> AutomatedJudge:
    if judge.judge_type is api.JudgeType.HUMAN:
        raise ValueError("Automated judge factory cannot instantiate human judge")
    if judge.judge_type is api.JudgeType.UNRECOGNIZED:
        raise ValueError("Cannot instantiate unrecognized judge type. Are you running an older version of AutoArena?")
    judge_class = (
        get_custom_judge_class(judge.name)
        if judge.judge_type is api.JudgeType.CUSTOM
        else AUTOMATED_JUDGE_TYPE_TO_CLASS[judge.judge_type]
    )
    if not issubclass(judge_class, AutomatedJudge) or judge.model_name is None or judge.system_prompt is None:
        raise ValueError(f"Misconfigured judge: {judge}")
    for wrapper in wrappers or []:
        judge_class = wrapper(judge_class)
    return judge_class(judge.name, judge.model_name, judge.system_prompt)


def verify_judge_type_environment(judge_type: api.JudgeType) -> None:
    if judge_type is api.JudgeType.UNRECOGNIZED:
        raise ValueError("Unable to run unrecognized judge type")
    judge_class = AUTOMATED_JUDGE_TYPE_TO_CLASS.get(judge_type, None)
    if judge_class is not None:
        judge_class.verify_environment()
