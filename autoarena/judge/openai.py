from autoarena.api import api
from autoarena.api.api import JudgeType
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import get_user_prompt, rate_limit, DEFAULT_BATCH_SIZE


class OpenAIJudge(AutomatedJudge):
    API_KEY_NAME = "OPENAI_API_KEY"

    def __init__(self, model_name: str, system_prompt: str) -> None:
        from openai import OpenAI

        super().__init__(model_name, system_prompt)
        self._client = OpenAI()

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.OPENAI

    @property
    def description(self) -> str:
        return f"OpenAI judge model '{self.name}'"

    # OpenAI has different tiers and different rate limits for different models, choose a safeish value
    @rate_limit(n_calls=1_000 // DEFAULT_BATCH_SIZE, n_seconds=60, n_call_buffer=50 // DEFAULT_BATCH_SIZE)
    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        return [self._judge_one(h2h) for h2h in batch]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=[
                dict(role="system", content=self.system_prompt),
                dict(role="user", content=get_user_prompt(h2h)),
            ],
        )
        return response.choices[0].message.content
