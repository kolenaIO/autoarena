import ollama

from autostack.api import api
from autostack.api.api import JudgeType
from autostack.judge.base import Judge
from autostack.judge.utils import BASIC_SYSTEM_PROMPT, get_user_prompt


class OllamaJudge(Judge):
    def __init__(self, model: str) -> None:
        self.model = model

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.OLLAMA

    @property
    def name(self) -> str:
        return self.model

    @property
    def description(self) -> str:
        return f"Ollama model '{self.model}'"

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        return [self._judge_one(h2h) for h2h in batch]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[
                dict(role="system", content=BASIC_SYSTEM_PROMPT),
                dict(role="user", content=get_user_prompt(h2h)),
            ],
        )
        return response["message"]["content"]
