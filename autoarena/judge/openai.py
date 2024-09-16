import time

import httpx
from loguru import logger
from openai import OpenAI
from pytimeparse.timeparse import timeparse

from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import get_user_prompt, rate_limit


class OpenAIJudge(AutomatedJudge):
    API_KEY_NAME = "OPENAI_API_KEY"

    def __init__(self, name: str, model_name: str, system_prompt: str) -> None:
        super().__init__(name, model_name, system_prompt)
        self._client = OpenAI()

    @staticmethod
    def verify_environment() -> None:
        OpenAI().models.list()

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
            timeout=httpx.Timeout(30),  # time out in 30 seconds
        )
        response = response_raw.parse()
        self.update_usage(response.usage.prompt_tokens, response.usage.completion_tokens, time.time() - t0)
        self._handle_rate_limit(dict(response_raw.headers))
        return response.choices[0].message.content

    # NOTE: ideally this would handle backoff for request rate limit, but the API surfaces the per-day, not the
    #  per-minute request rate limits and those aren't really actionable (hours until reset)
    @staticmethod
    def _handle_rate_limit(headers: dict[str, str]) -> None:
        try:
            request_limit = int(headers.get("x-ratelimit-remaining-requests", 1e6))
            if request_limit < 50:
                request_limit_reset = headers.get("x-ratelimit-reset-requests")
                logger.warning(
                    f"Approaching OpenAI request rate limit: {request_limit} remaining, resets in {request_limit_reset}"
                )
            token_limit = int(headers.get("x-ratelimit-remaining-tokens", 1e6))
            if token_limit < 5_000:
                token_limit_reset = headers.get("x-ratelimit-reset-tokens")
                logger.warning(
                    f"Approaching OpenAI token rate limit: {token_limit} remaining, backing off for {token_limit_reset}"
                )
                sleep_seconds = timeparse(token_limit_reset) or 0
                time.sleep(sleep_seconds)
        except Exception:  # don't let this crash the program as it's not clear that these headers are stable
            pass
