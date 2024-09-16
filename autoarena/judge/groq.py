import time

from groq import Groq

from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import rate_limit, get_user_prompt


class GroqJudge(AutomatedJudge):
    API_KEY_NAME = "GROQ_API_KEY"

    def __init__(self, name: str, model_name: str, system_prompt: str) -> None:
        super().__init__(name, model_name, system_prompt)
        self._client = Groq()

    @staticmethod
    def verify_environment() -> None:
        Groq().models.list()

    # OpenAI has different tiers and different rate limits for different models, choose a safeish value
    @rate_limit(n_calls=1_000, n_seconds=60)
    def judge(self, prompt: str, response_a: str, response_b: str) -> str:
        t0 = time.time()
        response_raw = self._client.chat.completions.with_raw_response.create(
            model=self.model_name,
            messages=[
                dict(role="system", content=self.system_prompt),
                dict(role="user", content=get_user_prompt(prompt, response_a, response_b)),
            ],
            max_tokens=self.MAX_TOKENS,
            # timeout=httpx.Timeout(30),  # time out in 30 seconds
        )
        response = response_raw.parse()
        self.update_usage(response.usage.prompt_tokens, response.usage.completion_tokens, time.time() - t0)
        return response.choices[0].message.content
