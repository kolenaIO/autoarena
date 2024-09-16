import time

import together

from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import rate_limit, get_user_prompt


class TogetherJudge(AutomatedJudge):
    API_KEY_NAME = "TOGETHER_API_KEY"

    def __init__(self, name: str, model_name: str, system_prompt: str) -> None:
        super().__init__(name, model_name, system_prompt)
        self._client = together.Client()

    @staticmethod
    def verify_environment() -> None:
        together.Client().models.list()

    @rate_limit(n_calls=10, n_seconds=1, n_call_buffer=2)
    def judge(self, prompt: str, response_a: str, response_b: str) -> str:
        t0 = time.time()
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=[
                dict(role="system", content=self.system_prompt),
                dict(role="user", content=get_user_prompt(prompt, response_a, response_b)),
            ],
            max_tokens=self.MAX_TOKENS,
        )
        self.update_usage(response.usage.prompt_tokens, response.usage.completion_tokens, time.time() - t0)
        return response.choices[0].message.content
