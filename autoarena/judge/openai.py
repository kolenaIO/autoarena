from openai import OpenAI

from autoarena.api import api
from autoarena.api.api import JudgeType
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import get_user_prompt, rate_limit


class OpenAIJudge(AutomatedJudge):
    API_KEY_NAME = "OPENAI_API_KEY"

    def __init__(self, model_name: str, system_prompt: str) -> None:
        super().__init__(model_name, system_prompt)
        self._client = OpenAI()

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.OPENAI

    @property
    def description(self) -> str:
        return f"OpenAI judge model '{self.name}'"

    @staticmethod
    def verify_environment() -> None:
        OpenAI().models.list()

    # OpenAI has different tiers and different rate limits for different models, choose a safeish value
    @rate_limit(n_calls=1_000, n_seconds=60)
    def judge(self, h2h: api.HeadToHead) -> str:
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=[
                dict(role="system", content=self.system_prompt),
                dict(role="user", content=get_user_prompt(h2h)),
            ],
        )
        return response.choices[0].message.content
