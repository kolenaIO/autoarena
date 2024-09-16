import time

from autoarena.judge.openai import OpenAIJudge
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

    # Groq has yet to open their paid tier, these are the severely rate limited free tier limits
    @rate_limit(n_calls=30, n_seconds=60, n_call_buffer=10)
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
        # TODO: extract this to somewhere shared
        OpenAIJudge._handle_rate_limit(dict(response_raw.headers))
        return response.choices[0].message.content
