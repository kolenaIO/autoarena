import anthropic

from autostack.api import api
from autostack.api.api import JudgeType
from autostack.judge.base import Judge
from autostack.judge.utils import BASIC_SYSTEM_PROMPT, get_user_prompt


class AnthropicJudge(Judge):
    def __init__(self, model: str) -> None:
        self.client = anthropic.Client()
        self.model = model

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.ANTHROPIC

    @property
    def name(self) -> str:
        return self.model

    @property
    def description(self) -> str:
        return f"Anthropic judge model '{self.model}'"

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        return [self._judge_one(h2h) for h2h in batch]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        response = self.client.messages.create(
            model=self.model,
            system=BASIC_SYSTEM_PROMPT,
            messages=[dict(role="user", content=get_user_prompt(h2h))],
            max_tokens=10,  # should really just need 1
        )
        return response.content[0].text
