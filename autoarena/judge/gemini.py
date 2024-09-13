import os

import google.generativeai as genai

from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import get_user_prompt, JOINED_PROMPT_TEMPLATE, rate_limit


class GeminiJudge(AutomatedJudge):
    API_KEY_NAME = "GOOGLE_API_KEY"

    def __init__(self, model_name: str, system_prompt: str) -> None:
        super().__init__(model_name, system_prompt)
        genai.configure(api_key=os.environ.get(GeminiJudge.API_KEY_NAME, None))
        self._model = genai.GenerativeModel(model_name)

    @staticmethod
    def verify_environment() -> None:
        genai.configure(api_key=os.environ.get(GeminiJudge.API_KEY_NAME, None))
        # TODO: this takes a while, likely due to retries -- haven't figured out how to disable
        list(genai.list_models(page_size=1))

    @rate_limit(n_calls=1_000, n_seconds=60)
    def judge(self, prompt: str, response_a: str, response_b: str) -> str:
        user_prompt = get_user_prompt(prompt, response_a, response_b)
        full_prompt = JOINED_PROMPT_TEMPLATE.format(system_prompt=self.system_prompt, user_prompt=user_prompt)
        response = self._model.generate_content(
            full_prompt,
            generation_config=dict(max_output_tokens=self.MAX_TOKENS, temperature=0.0),
            # there's a gremlin here where some responses are still blocked for safety despite these settings
            safety_settings={
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            },
        )
        self.n_calls += 1
        self.total_input_tokens += response.usage_metadata.prompt_token_count
        self.total_output_tokens += response.usage_metadata.candidates_token_count
        return response.text
