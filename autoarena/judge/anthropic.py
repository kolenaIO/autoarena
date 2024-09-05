from autoarena.api import api
from autoarena.api.api import JudgeType
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import get_user_prompt, rate_limit, DEFAULT_BATCH_SIZE


class AnthropicJudge(AutomatedJudge):
    API_KEY_NAME = "ANTHROPIC_API_KEY"

    def __init__(self, model_name: str, system_prompt: str) -> None:
        import anthropic

        super().__init__(model_name, system_prompt)
        self._client = anthropic.Client()

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.ANTHROPIC

    @property
    def description(self) -> str:
        return f"Anthropic judge model '{self.name}'"

    # anthropic has different tiers with 1000/2000/4000, opting to be conservative by default
    @rate_limit(n_calls=1_000 // DEFAULT_BATCH_SIZE, n_seconds=60, n_call_buffer=50 // DEFAULT_BATCH_SIZE)
    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        return [self._judge_one(h2h) for h2h in batch]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        response = self._client.messages.create(
            model=self.model_name,
            system=self.system_prompt,
            messages=[dict(role="user", content=get_user_prompt(h2h))],
            max_tokens=10,  # should really just need 1
        )
        return response.content[0].text
