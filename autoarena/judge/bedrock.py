from autoarena.api import api
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import DEFAULT_BATCH_SIZE, rate_limit, get_user_prompt, DEFAULT_MAX_TOKENS


class BedrockJudge(AutomatedJudge):
    API_KEY_NAME = None

    def __init__(self, model_name: str, system_prompt: str) -> None:
        import boto3

        super().__init__(model_name, system_prompt)
        region_name = "us-east-1"  # TODO: how to configure this?
        self._client = boto3.client(service_name="bedrock-runtime", region_name=region_name)

    @property
    def judge_type(self) -> api.JudgeType:
        return api.JudgeType.BEDROCK

    @property
    def description(self) -> str:
        return f"AWS Bedrock judge model '{self.name}'"

    # TODO: look these up
    @rate_limit(n_calls=1_000 // DEFAULT_BATCH_SIZE, n_seconds=60, n_call_buffer=50 // DEFAULT_BATCH_SIZE)
    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        return [self._judge_one(h2h) for h2h in batch]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        response = self._client.converse(
            modelId=self.model_name,
            system=[dict(text=self.system_prompt)],
            messages=[dict(role="user", content=[dict(text=get_user_prompt(h2h))])],
            inferenceConfig=dict(maxTokens=DEFAULT_MAX_TOKENS),
        )
        return response["output"]["message"]["content"][0]["text"]
