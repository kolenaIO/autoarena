from autoarena.api import api
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import rate_limit, get_user_prompt


class TogetherJudge(AutomatedJudge):
    API_KEY_NAME = "TOGETHER_API_KEY"

    def __init__(self, model_name: str, system_prompt: str) -> None:
        import together

        super().__init__(model_name, system_prompt)
        self._client = together.Client()

    @property
    def judge_type(self) -> api.JudgeType:
        return api.JudgeType.COHERE

    @property
    def description(self) -> str:
        return f"Together AI judge model '{self.name}'"

    @rate_limit(n_calls=10, n_seconds=1, n_call_buffer=2)
    def judge(self, h2h: api.HeadToHead) -> str:
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=[
                dict(role="system", content=self.system_prompt),
                dict(role="user", content=get_user_prompt(h2h)),
            ],
            max_tokens=12,
        )
        return response.choices[0].message.content
