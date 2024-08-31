from openai import OpenAI
from tqdm import tqdm

from autostack.api import api
from autostack.api.api import JudgeType
from autostack.judge.base import Judge
from autostack.judge.utils import BASIC_SYSTEM_PROMPT, get_user_prompt


class OpenAIJudge(Judge):
    def __init__(self, model: str) -> None:
        self.client = OpenAI()
        self.model = model

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.OPENAI

    @property
    def name(self) -> str:
        return self.model

    @property
    def description(self) -> str:
        return f"OpenAI judge model '{self.model}'"

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        return [self._judge_one(h2h) for h2h in tqdm(batch, desc=self.name)]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                dict(role="system", content=BASIC_SYSTEM_PROMPT),
                dict(role="user", content=get_user_prompt(h2h)),
            ],
        )
        return response.choices[0].message.content
