import sys

import numpy as np

from autostack.api import api
from autostack.api.api import JudgeType
from autostack.judge.base import Judge

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

JOINED_PROMPT_TEMPLATE = """\
<|Start of System Prompt|>
{system_prompt}
<|End of System Prompt|>

{user_prompt}"""

ACCEPTABLE_RESPONSES = {"A", "B", "-"}


def get_user_prompt(h2h: api.HeadToHead) -> str:
    return USER_PROMPT_TEMPLATE.format(prompt=h2h.prompt, response_a=h2h.response_a, response_b=h2h.response_b)


class ABShufflingJudge(Judge):
    """Randomly shuffles which is A and which is B before passing to another judge."""

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


def clean_judgement(winner: str) -> str:
    return winner.strip(" \t\n'\"*.")  # strip common formatting issues


class CleaningJudge(Judge):
    """Attempt to clean raw responses from other judges"""

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
        cleaned = []
        for winner_raw in self.judge.judge_batch(batch):
            winner = clean_judgement(winner_raw)
            if winner in ACCEPTABLE_RESPONSES:
                cleaned.append(winner)
            else:
                message = f"[{self.__class__.__name__}] Saving bad response from '{self.name}' as tie: {winner_raw}"
                print(message, file=sys.stderr)
                cleaned.append("-")
        return cleaned


class FixingJudge(Judge):
    """If the response does not fit nicely into the expected "A", "B", "-" format, classify it"""

    CLASSIFIER_MODEL = "MoritzLaurer/deberta-v3-xsmall-zeroshot-v1.1-all-33"
    A_IS_BETTER = "A is better"
    B_IS_BETTER = "B is better"
    TIE = "Neither is better / Both are good (Tie)"
    CLASSES = [A_IS_BETTER, B_IS_BETTER, TIE]
    CLASS_TO_WINNER = {A_IS_BETTER: "A", B_IS_BETTER: "B", TIE: "-"}

    def __init__(self, judge: Judge):
        from transformers import pipeline

        self.pipe = pipeline(model=self.CLASSIFIER_MODEL)
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
        cleaned = []
        for winner_raw in self.judge.judge_batch(batch):
            winner = clean_judgement(winner_raw)
            if winner not in ACCEPTABLE_RESPONSES:
                classifications = self.pipe(winner_raw, candidate_labels=self.CLASSES)
                winner = self.CLASS_TO_WINNER[classifications["labels"][0]]
                print(f"Fixed bad response: '{winner_raw}' as '{winner}'", file=sys.stderr)
            cleaned.append(winner)
        return cleaned
