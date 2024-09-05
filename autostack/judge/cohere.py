from autostack.api import api
from autostack.api.api import JudgeType
from autostack.judge.base import AutomatedJudge
from autostack.judge.utils import get_user_prompt, rate_limit


class CohereJudge(AutomatedJudge):
    API_KEY_NAME = "COHERE_API_KEY"  # TODO: also support "CO_API_KEY"?

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

    # TODO: baking batch size of 8 in here is not great
    @rate_limit(n_calls=1_000 // 8, n_seconds=60, n_call_buffer=50 // 8)
    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        return [self._judge_one(h2h) for h2h in batch]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        response = self._client.chat(
            model=self.model_name,
            preamble=self.system_prompt,
            message=get_user_prompt(h2h),
            max_tokens=12,
        )
        return response.text
