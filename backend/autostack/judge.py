from abc import ABCMeta, abstractmethod
from typing import Literal

from openai import OpenAI
from tqdm import tqdm

from autostack.api import api as API


class Judge(metaclass=ABCMeta):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def judge_batch(self, batch: list[API.HeadToHead]) -> list[str]:  # TODO: return more information than just winner?
        ...


class OpenAIJudge(Judge):
    SYSTEM_PROMPT = """\
You are a human preference judge tasked with deciding which of the two assistant responses, A or B, better responds to the user's prompt.

Respond with ONLY "A" if assistant A is better, "B" if assistant B is better, or "-" if neither is better than the other."""

    USER_PROMPT_TEMPLATE = """\
<|Start of User Prompt|>
{prompt}
<|End of User Prompt|>

<|Start of Assistant A's Response|>
{response_a}
<|End of Assistant A's Response|>

<|Start of Assistant B's Response|>
{response_b}
<|End of Assistant B's Response|>"""

    def __init__(self, model: Literal["gpt-4o-mini", "gpt-4o"]) -> None:
        self.client = OpenAI()
        self.model = model

    @property
    def name(self) -> str:
        return self.model

    @property
    def description(self) -> str:
        return f"OpenAI judge model '{self.model}'"

    def judge_batch(self, batch: list[API.HeadToHead]) -> list[str]:
        name = f"{self.__class__.__name__}({self.model})"
        return [self._judge_one(h2h) for h2h in tqdm(batch, desc=name)]

    def _judge_one(self, h2h: API.HeadToHead) -> str:
        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            prompt=h2h.prompt,
            response_a=h2h.response_a,
            response_b=h2h.response_b,
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                dict(role="system", content=self.SYSTEM_PROMPT),
                dict(role="user", content=user_prompt),
            ],
        )
        return response.choices[0].message.content
