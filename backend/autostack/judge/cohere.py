import cohere

from autostack.api import api
from autostack.api.api import JudgeType
from autostack.judge.base import Judge
from autostack.judge.utils import BASIC_SYSTEM_PROMPT, get_user_prompt


class CohereJudge(Judge):
    def __init__(self, model: str) -> None:
        self.client = cohere.Client()
        self.model = model

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.COHERE

    @property
    def name(self) -> str:
        return self.model

    @property
    def description(self) -> str:
        return f"Cohere judge model '{self.model}'"

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        return [self._judge_one(h2h) for h2h in batch]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        response = self.client.chat(model=self.model, preamble=BASIC_SYSTEM_PROMPT, message=get_user_prompt(h2h))
        return response.text
