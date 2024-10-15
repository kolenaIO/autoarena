from enum import Enum
import os
from typing import Dict
import anthropic
import cohere
import google.generativeai as genai
from openai import OpenAI
from together import Together


class Model(str, Enum):
    o1_mini = "o1-mini"
    o1_preview = "o1-preview"
    gpt_4o_mini = "gpt-4o-mini"
    gpt_4o = "gpt-4o"
    gemini_1_5_pro_002 = "gemini-1.5-pro-002"
    claude_3_5_sonnet_20240620 = "claude-3-5-sonnet-20240620"
    command_r_08_2024 = "command-r-08-2024"
    llama_3_2_90B = "Llama-3.2-90B-Vision-Instruct-Turbo"


class AskLLM:
    def __init__(self, model_choice: Model, api_keys: Dict[str, str]):
        self.model = model_choice
        self.api_keys = api_keys

        if model_choice in {Model.o1_mini, Model.o1_preview, Model.gpt_4o_mini, Model.gpt_4o}:
            self.client = OpenAI(api_key=self.api_keys["OPENAI"])

        elif model_choice == Model.gemini_1_5_pro_002:
            genai.configure(api_key=self.api_keys["GOOGLE"])
            self.google_model = genai.GenerativeModel(model_choice.value)
            self.safety_settings = {
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            }
            self.generation_config = {
                "max_output_tokens": 1024,
            }

        elif model_choice == Model.claude_3_5_sonnet_20240620:
            self.client = anthropic.Anthropic(api_key=self.api_keys["ANTHROPIC"])

        elif model_choice == Model.command_r_08_2024:
            self.client = cohere.Client(api_keys["COHERE"])

        elif model_choice == Model.llama_3_2_90B:
            self.client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

    def get_api_result(self, question: str) -> str:
        if self.model in {Model.gpt_4o_mini, Model.gpt_4o}:
            return (
                self.client.chat.completions.create(
                    model=self.model.value,
                    messages=[{"role": "user", "content": question}],
                    max_completion_tokens=1024,
                )
                .choices[0]
                .message.content
            )

        elif self.model in {Model.o1_mini, Model.o1_preview}:
            return (
                self.client.chat.completions.create(
                    model=self.model.value,
                    messages=[{"role": "user", "content": question}],
                    max_completion_tokens=2048,
                )
                .choices[0]
                .message.content
            )

        elif self.model == Model.gemini_1_5_pro_002:
            return self.google_model.generate_content(
                question,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
                stream=False,
            ).text

        elif self.model == Model.claude_3_5_sonnet_20240620:
            return (
                self.client.messages.create(
                    model=self.model.value,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": question}],
                )
                .content[0]
                .text
            )

        elif self.model == Model.command_r_08_2024:
            return self.client.chat(
                model=self.model.value,
                max_tokens=1024,
                message=question,
            ).text

        elif self.model == Model.llama_3_2_90B:
            response = self.client.chat.completions.create(
                model="meta-llama/" + self.model.value,
                messages=[{"role": "user", "content": question}],
                max_tokens=1024,
                stream=False,
            )
            return response.choices[0].message.content

        return "<MODEL ABSENT ERROR>"
