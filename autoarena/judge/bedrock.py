import boto3

from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import rate_limit, get_user_prompt


class BedrockJudge(AutomatedJudge):
    API_KEY_NAME = None

    def __init__(self, model_name: str, system_prompt: str) -> None:
        super().__init__(model_name, system_prompt)
        self._client = boto3.client(service_name="bedrock-runtime")

    @staticmethod
    def verify_environment() -> None:
        boto3.client(service_name="sts").get_caller_identity()

    @rate_limit(n_calls=200, n_seconds=1, n_call_buffer=25)
    def judge(self, prompt: str, response_a: str, response_b: str) -> str:
        response = self._client.converse(
            modelId=self.model_name,
            system=[dict(text=self.system_prompt)],
            messages=[dict(role="user", content=[dict(text=get_user_prompt(prompt, response_a, response_b))])],
            inferenceConfig=dict(maxTokens=self.MAX_TOKENS),
        )
        self.n_calls += 1
        self.total_input_tokens += response["usage"]["inputTokens"]
        self.total_output_tokens += response["usage"]["outputTokens"]
        return response["output"]["message"]["content"][0]["text"]
