from abc import ABCMeta, abstractmethod
from typing import Literal

import numpy as np
import ollama
from openai import OpenAI
from tqdm import tqdm

from autostack.api import api
from autostack.api.api import JudgeType


class Judge(metaclass=ABCMeta):
    @property
    @abstractmethod
    def judge_type(self) -> JudgeType:
        """Enum type for this judge, e.g. 'human' or 'ollama'"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this judge, e.g. 'GPT-4o mini'"""

    @property
    @abstractmethod
    def description(self) -> str:
        """Freeform description for this judge, usually ending without a period"""

    @abstractmethod
    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:  # TODO: return more information than just winner?
        ...


class HumanJudge(Judge):
    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.HUMAN

    @property
    def name(self) -> str:
        return "Human"

    @property
    def description(self) -> str:
        return "Manual ratings submitted via the 'Head-to-Head' tab"

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:  # TODO: return more information than just winner?
        raise NotImplementedError


BASIC_SYSTEM_PROMPT = """\
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


class ABShufflingJudge(Judge):
    def __init__(self, judge: Judge):
        self.judge = judge

    @property
    def judge_type(self) -> JudgeType:
        return self.judge.judge_type

    @property
    def name(self) -> str:
        return self.judge.name

    @property
    def description(self) -> str:
        return self.judge.description

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        shuffles = np.random.randint(2, size=len(batch)) < 1
        shuffled_batch = [h2h if shuffle else self._shuffle_h2h(h2h) for h2h, shuffle in zip(batch, shuffles)]
        winners = self.judge.judge_batch(shuffled_batch)
        return [winner if shuffle else self._shuffle_winner(winner) for winner, shuffle in zip(winners, shuffles)]

    @staticmethod
    def _shuffle_h2h(h2h: api.HeadToHead) -> api.HeadToHead:
        return api.HeadToHead(
            prompt=h2h.prompt,
            result_a_id=h2h.result_b_id,
            response_a=h2h.response_b,
            result_b_id=h2h.result_a_id,
            response_b=h2h.response_a,
        )

    @staticmethod
    def _shuffle_winner(winner: str) -> str:
        return "B" if winner == "A" else "A" if winner == "B" else "-"


class OpenAIJudge(Judge):
    def __init__(self, model: Literal["gpt-4o-mini", "gpt-4o"]) -> None:
        self.client = OpenAI()
        self.model = model

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.OPENAI

    @property
    def name(self) -> str:
        return self.model

    @property
    def description(self) -> str:
        return f"OpenAI judge model '{self.model}'"

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        name = f"{self.__class__.__name__}({self.model})"
        return [self._judge_one(h2h) for h2h in tqdm(batch, desc=name)]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        user_prompt = USER_PROMPT_TEMPLATE.format(
            prompt=h2h.prompt,
            response_a=h2h.response_a,
            response_b=h2h.response_b,
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                dict(role="system", content=BASIC_SYSTEM_PROMPT),
                dict(role="user", content=user_prompt),
            ],
        )
        return response.choices[0].message.content


class OllamaJudge(Judge):
    def __init__(self, model: str) -> None:
        self.model = model

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.OLLAMA

    @property
    def name(self) -> str:
        return self.model

    @property
    def description(self) -> str:
        return f"Ollama model '{self.model}'"

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        name = f"{self.__class__.__name__}({self.model})"
        return [self._judge_one(h2h) for h2h in tqdm(batch, desc=name)]

    def _judge_one(self, h2h: api.HeadToHead) -> str:
        user_prompt = USER_PROMPT_TEMPLATE.format(
            prompt=h2h.prompt,
            response_a=h2h.response_a,
            response_b=h2h.response_b,
        )
        response = ollama.chat(
            model=self.model,
            messages=[
                dict(role="system", content=BASIC_SYSTEM_PROMPT),
                dict(role="user", content=user_prompt),
            ],
        )
        return response["message"]["content"]


def judge_factory(judge: api.Judge) -> Judge:
    if judge.judge_type is JudgeType.HUMAN:
        return HumanJudge()
    if judge.judge_type is JudgeType.OLLAMA:
        return OllamaJudge(judge.name)  # TODO: should this be stored elsewhere?
    if judge.judge_type is JudgeType.OPENAI:
        return OpenAIJudge(judge.name)  # type: ignore
    raise ValueError(f"unable to instantiate judge: {judge}")


# TODO: remove this little script, convenience for running prompts
if __name__ == "__main__":
    import pandas as pd

    df = pd.read_csv("prompts.csv").iloc[:25]
    # client = OpenAI()
    model = "gemma2:9b"
    out = []
    for r in tqdm(df.itertuples(), total=len(df)):
        # response = client.chat.completions.create(model="gpt-4o-mini", messages=[dict(role="user", content=r.prompt)])
        # out.append(response.choices[0].message.content)
        response = ollama.chat(model=model, messages=[dict(role="user", content=r.prompt)])
        out.append(response["message"]["content"])
    df["model"] = model
    df["response"] = out
    df.to_csv(f"{model}.csv", index=False)
