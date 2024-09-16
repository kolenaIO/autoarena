import httpx
import ollama

from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import get_user_prompt, warn_if_slow


class OllamaJudge(AutomatedJudge):
    API_KEY_NAME = None  # does not require an API key

    def __init__(self, name: str, model_name: str, system_prompt: str) -> None:
        super().__init__(name, model_name, system_prompt)
        self._client = ollama
        try:
            self._client.show(model_name)  # ensure this model exists and is pulled
        except ollama.ResponseError:
            raise RuntimeError(f"Ollama model '{model_name}' not found, try pulling it first with 'ollama pull'")
        except httpx.ConnectError:
            raise RuntimeError("Unable to connect to Ollama, ensure it is running on the same host running AutoArena")

    @staticmethod
    def verify_environment() -> None:
        try:
            ollama.list()
        except httpx.ConnectError:
            raise RuntimeError("Unable to connect to Ollama, ensure it is running on the same host running AutoArena")

    @warn_if_slow(slow_threshold_seconds=5)
    def judge(self, prompt: str, response_a: str, response_b: str) -> str:
        response = self._client.chat(
            model=self.model_name,
            messages=[
                dict(role="system", content=self.system_prompt),
                dict(role="user", content=get_user_prompt(prompt, response_a, response_b)),
            ],
            options=dict(temperature=0, seed=0, num_predict=self.MAX_TOKENS),
        )
        self.update_usage(response["prompt_eval_count"], response["eval_count"])
        return response["message"]["content"]
