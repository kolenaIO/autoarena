import google.generativeai as genai

from autostack.api import api
from autostack.api.api import JudgeType
from autostack.judge.base import Judge
from autostack.judge.utils import BASIC_SYSTEM_PROMPT, get_user_prompt, JOINED_PROMPT_TEMPLATE


class GeminiJudge(Judge):
    def __init__(self, model_name: str) -> None:
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.GEMINI

    @property
    def name(self) -> str:
        return self.model_name

    @property
    def description(self) -> str:
        return f"Google Gemini judge model '{self.model_name}'"

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        return [self._judge_one(h2h) for h2h in batch]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        prompt = JOINED_PROMPT_TEMPLATE.format(system_prompt=BASIC_SYSTEM_PROMPT, user_prompt=get_user_prompt(h2h))
        response = self.model.generate_content(
            prompt,
            generation_config=dict(max_output_tokens=12, temperature=0.0),
            safety_settings={
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            },
        )
        return response.text
