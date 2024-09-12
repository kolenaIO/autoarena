import cohere

from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import get_user_prompt, rate_limit


class CohereJudge(AutomatedJudge):
    API_KEY_NAME = "COHERE_API_KEY"  # TODO: also support "CO_API_KEY"?

    def __init__(self, model_name: str, system_prompt: str) -> None:
        super().__init__(model_name, system_prompt)
        self._client = cohere.Client()

    @staticmethod
    def verify_environment() -> None:
        cohere.Client().models.list()

    @rate_limit(n_calls=1_000, n_seconds=60)
    def judge(self, prompt: str, response_a: str, response_b: str) -> str:
        response = self._client.chat(
            model=self.model_name,
            preamble=self.system_prompt,
            message=get_user_prompt(prompt, response_a, response_b),
            max_tokens=self.MAX_TOKENS,
        )
        self.n_calls += 1
        self.total_input_tokens += int(response.meta.billed_units.input_tokens)
        self.total_output_tokens += int(response.meta.billed_units.output_tokens)
        return response.text
