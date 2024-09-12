import time

from loguru import logger
from openai import OpenAI
from pytimeparse.timeparse import timeparse

from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import get_user_prompt, rate_limit


class OpenAIJudge(AutomatedJudge):
    API_KEY_NAME = "OPENAI_API_KEY"

    def __init__(self, model_name: str, system_prompt: str) -> None:
        super().__init__(model_name, system_prompt)
        self._client = OpenAI()

    @staticmethod
    def verify_environment() -> None:
        OpenAI().models.list()

    # OpenAI has different tiers and different rate limits for different models, choose a safeish value
    @rate_limit(n_calls=1_000, n_seconds=60)
    def judge(self, prompt: str, response_a: str, response_b: str) -> str:
        response_raw = self._client.chat.completions.with_raw_response.create(
            model=self.model_name,
            messages=[
                dict(role="system", content=self.system_prompt),
                dict(role="user", content=get_user_prompt(prompt, response_a, response_b)),
            ],
            max_tokens=self.MAX_TOKENS,
        )
        request_limit = int(response_raw.headers.get("x-ratelimit-remaining-requests", 1e6))
        if request_limit < 50:
            request_limit_reset = response_raw.headers.get("x-ratelimit-reset-requests")
            logger.warning(
                f"Approaching OpenAI request rate limit: {request_limit} remaining, resets in {request_limit_reset}"
            )
        token_limit = int(response_raw.headers.get("x-ratelimit-remaining-tokens", 1e6))
        if token_limit < 5_000:
            token_limit_reset = response_raw.headers.get("x-ratelimit-reset-tokens")
            logger.warning(
                f"Approaching OpenAI token rate limit: {token_limit} remaining, backing off for {token_limit_reset}"
            )
            time.sleep(timeparse(token_limit_reset))
        response = response_raw.parse()
        self.n_calls += 1
        self.total_input_tokens += response.usage.prompt_tokens
        self.total_output_tokens += response.usage.completion_tokens
        return response.choices[0].message.content
