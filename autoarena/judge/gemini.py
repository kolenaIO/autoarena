from autoarena.api import api
from autoarena.api.api import JudgeType
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import get_user_prompt, JOINED_PROMPT_TEMPLATE, rate_limit, DEFAULT_BATCH_SIZE


class GeminiJudge(AutomatedJudge):
    API_KEY_NAME = "GOOGLE_API_KEY"

    def __init__(self, model_name: str, system_prompt: str) -> None:
        import google.generativeai as genai

        super().__init__(model_name, system_prompt)
        self._model = genai.GenerativeModel(model_name)

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.GEMINI

    @property
    def description(self) -> str:
        return f"Google Gemini judge model '{self.name}'"

    @rate_limit(n_calls=1_000 // DEFAULT_BATCH_SIZE, n_seconds=60, n_call_buffer=50 // DEFAULT_BATCH_SIZE)
    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        return [self._judge_one(h2h) for h2h in batch]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        import google.generativeai as genai

        prompt = JOINED_PROMPT_TEMPLATE.format(system_prompt=self.system_prompt, user_prompt=get_user_prompt(h2h))
        response = self._model.generate_content(
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
