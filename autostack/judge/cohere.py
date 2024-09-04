from autostack.api import api
from autostack.api.api import JudgeType
from autostack.judge.base import AutomatedJudge
from autostack.judge.utils import get_user_prompt


class CohereJudge(AutomatedJudge):
    def __init__(self, model_name: str, system_prompt: str) -> None:
        import cohere

        super().__init__(model_name, system_prompt)
        self._client = cohere.Client()

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.COHERE

    @property
    def description(self) -> str:
        return f"Cohere judge model '{self.name}'"

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        return [self._judge_one(h2h) for h2h in batch]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        response = self._client.chat(model=self.model_name, preamble=self.system_prompt, message=get_user_prompt(h2h))
        return response.text
