import httpx
import ollama

from autoarena.api import api
from autoarena.api.api import JudgeType
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import get_user_prompt


class OllamaJudge(AutomatedJudge):
    API_KEY_NAME = None  # does not require an API key

    def __init__(self, model_name: str, system_prompt: str) -> None:
        super().__init__(model_name, system_prompt)
        self._client = ollama
        try:
            self._client.show(model_name)  # ensure this model exists and is pulled
        except ollama.ResponseError:
            raise RuntimeError(f"Ollama model '{model_name}' not found, try pulling it first with 'ollama pull'")
        except httpx.ConnectError:
            raise RuntimeError("Unable to connect to Ollama, ensure it is running on the same host running AutoArena")

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.OLLAMA

    @property
    def description(self) -> str:
        return f"Ollama model '{self.name}'"

    @staticmethod
    def verify_environment() -> None:
        try:
            ollama.list()
        except httpx.ConnectError:
            raise RuntimeError("Unable to connect to Ollama, ensure it is running on the same host running AutoArena")

    def judge(self, h2h: api.HeadToHead) -> str:
        response = self._client.chat(
            model=self.model_name,
            messages=[
                dict(role="system", content=self.system_prompt),
                dict(role="user", content=get_user_prompt(h2h)),
            ],
            options=dict(temperature=0, seed=0),
        )
        return response["message"]["content"]
