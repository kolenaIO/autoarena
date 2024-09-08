import os

import google.generativeai as genai

from autoarena.api import api
from autoarena.api.api import JudgeType
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import get_user_prompt, JOINED_PROMPT_TEMPLATE, rate_limit, DEFAULT_MAX_TOKENS


class GeminiJudge(AutomatedJudge):
    API_KEY_NAME = "GOOGLE_API_KEY"
    MAX_TOKENS = DEFAULT_MAX_TOKENS

    def __init__(self, model_name: str, system_prompt: str) -> None:
        super().__init__(model_name, system_prompt)
        genai.configure(api_key=os.environ.get(GeminiJudge.API_KEY_NAME, None))
        self._model = genai.GenerativeModel(model_name)

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.GEMINI

    @property
    def description(self) -> str:
        return f"Google Gemini judge model '{self.name}'"

    @staticmethod
    def verify_environment() -> None:
        genai.configure(api_key=os.environ.get(GeminiJudge.API_KEY_NAME, None))
        # TODO: this takes a while, likely due to retries -- haven't figured out how to disable
        list(genai.list_models(page_size=1))

    @rate_limit(n_calls=1_000, n_seconds=60)
    def judge(self, h2h: api.HeadToHead) -> str:
        prompt = JOINED_PROMPT_TEMPLATE.format(system_prompt=self.system_prompt, user_prompt=get_user_prompt(h2h))
        response = self._model.generate_content(
            prompt,
            generation_config=dict(max_output_tokens=self.MAX_TOKENS, temperature=0.0),
            safety_settings={
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            },
        )
        return response.text
