import time

from autoarena.judge.base import AutomatedJudge

from huggingface_hub import InferenceClient

from autoarena.judge.utils import get_user_prompt


class HuggingFaceJudge(AutomatedJudge):
    def __init__(self, name: str, model_name: str, system_prompt: str):
        super().__init__(name, model_name, system_prompt)
        self._client = InferenceClient(model_name)

    @staticmethod
    def verify_environment() -> None: ...  # TODO

    def judge(self, prompt: str, response_a: str, response_b: str) -> str:
        t0 = time.time()
        response = self._client.chat_completion(
            messages=[
                dict(role="system", content=self.system_prompt),
                dict(role="user", content=get_user_prompt(prompt, response_a, response_b)),
            ]
        )
        self.update_usage(response.usage.prompt_tokens, response.usage.completion_tokens, time.time() - t0)
        return response.choices[0].message.content
