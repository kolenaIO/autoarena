import anthropic

from autoarena.api import api
from autoarena.api.api import JudgeType
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import get_user_prompt, rate_limit


class AnthropicJudge(AutomatedJudge):
    API_KEY_NAME = "ANTHROPIC_API_KEY"

    def __init__(self, model_name: str, system_prompt: str) -> None:
        super().__init__(model_name, system_prompt)
        self._client = anthropic.Client()

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.ANTHROPIC

    @property
    def description(self) -> str:
        return f"Anthropic judge model '{self.name}'"

    @staticmethod
    def verify_environment() -> None:
        # this is a little dirty, but gets the job done as requests without valid auth are rejected eagerly
        try:
            anthropic.Client().post("/v1/messages", cast_to=object)
        except (anthropic.AuthenticationError, TypeError) as e:
            raise e
        except Exception:
            pass

    # anthropic has different tiers with 1000/2000/4000, opting to be conservative by default
    @rate_limit(n_calls=1_000, n_seconds=60)
    def judge(self, h2h: api.HeadToHead) -> str:
        response = self._client.messages.create(
            model=self.model_name,
            system=self.system_prompt,
            messages=[dict(role="user", content=get_user_prompt(h2h))],
            max_tokens=10,  # should really just need 1
        )
        return response.content[0].text
