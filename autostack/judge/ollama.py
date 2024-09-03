from autostack.api import api
from autostack.api.api import JudgeType
from autostack.judge.base import Judge
from autostack.judge.utils import get_user_prompt


class OllamaJudge(Judge):
    def __init__(self, model_name: str, system_prompt: str) -> None:
        import ollama

        self._client = ollama
        self._model_name = model_name
        self._system_prompt = system_prompt

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.OLLAMA

    @property
    def name(self) -> str:
        return self._model_name

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @property
    def description(self) -> str:
        return f"Ollama model '{self.name}'"

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        return [self._judge_one(h2h) for h2h in batch]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        response = self._client.chat(
            model=self.model_name,
            messages=[
                dict(role="system", content=self.system_prompt),
                dict(role="user", content=get_user_prompt(h2h)),
            ],
        )
        return response["message"]["content"]
