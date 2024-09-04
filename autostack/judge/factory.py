from autostack.api import api
from autostack.api.api import JudgeType
from autostack.judge.anthropic import AnthropicJudge
from autostack.judge.base import Judge
from autostack.judge.cohere import CohereJudge
from autostack.judge.gemini import GeminiJudge
from autostack.judge.human import HumanJudge
from autostack.judge.ollama import OllamaJudge
from autostack.judge.openai import OpenAIJudge


def judge_factory(judge: api.Judge) -> Judge:
    if judge.judge_type is JudgeType.HUMAN:
        return HumanJudge()
    if judge.judge_type is JudgeType.CUSTOM:
        raise NotImplementedError(f"judge type '{judge.judge_type}' not yet implemented")
    if judge.model_name is None or judge.system_prompt is None:
        raise ValueError(f"misconfigured judge: {judge}")
    if judge.judge_type is JudgeType.OLLAMA:
        return OllamaJudge(judge.model_name, judge.system_prompt)
    if judge.judge_type is JudgeType.OPENAI:
        return OpenAIJudge(judge.model_name, judge.system_prompt)
    if judge.judge_type is JudgeType.ANTHROPIC:
        return AnthropicJudge(judge.model_name, judge.system_prompt)
    if judge.judge_type is JudgeType.COHERE:
        return CohereJudge(judge.model_name, judge.system_prompt)
    if judge.judge_type is JudgeType.GEMINI:
        return GeminiJudge(judge.model_name, judge.system_prompt)
    raise ValueError(f"unrecognized judge type: {judge}")
