import boto3

from autoarena.api import api
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import rate_limit, get_user_prompt, DEFAULT_MAX_TOKENS


class BedrockJudge(AutomatedJudge):
    API_KEY_NAME = None

    def __init__(self, model_name: str, system_prompt: str) -> None:
        super().__init__(model_name, system_prompt)
        self._client = boto3.client(service_name="bedrock-runtime")

    @property
    def judge_type(self) -> api.JudgeType:
        return api.JudgeType.BEDROCK

    @property
    def description(self) -> str:
        return f"AWS Bedrock judge model '{self.name}'"

    @staticmethod
    def verify_environment() -> None:
        boto3.client(service_name="sts").get_caller_identity()

    @rate_limit(n_calls=200, n_seconds=1, n_call_buffer=25)
    def judge(self, h2h: api.HeadToHead) -> str:
        response = self._client.converse(
            modelId=self.model_name,
            system=[dict(text=self.system_prompt)],
            messages=[dict(role="user", content=[dict(text=get_user_prompt(h2h))])],
            inferenceConfig=dict(maxTokens=DEFAULT_MAX_TOKENS),
        )
        return response["output"]["message"]["content"][0]["text"]
