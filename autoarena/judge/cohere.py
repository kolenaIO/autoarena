import time

import cohere

from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import get_user_prompt, rate_limit


class CohereJudge(AutomatedJudge):
    API_KEY_NAME = "COHERE_API_KEY"  # TODO: also support "CO_API_KEY"?

    def __init__(self, name: str, model_name: str, system_prompt: str) -> None:
        super().__init__(name, model_name, system_prompt)
        self._client = cohere.Client()

    @staticmethod
    def verify_environment() -> None:
        cohere.Client().models.list()

    @rate_limit(n_calls=1_000, n_seconds=60)
    def judge(self, prompt: str, response_a: str, response_b: str) -> str:
        t0 = time.time()
        response = self._client.chat(
            model=self.model_name,
            preamble=self.system_prompt,
            message=get_user_prompt(prompt, response_a, response_b),
            max_tokens=self.MAX_TOKENS,
        )
        self.update_usage(
            int(response.meta.billed_units.input_tokens),
            int(response.meta.billed_units.output_tokens),
            time.time() - t0,
        )
        return response.text
