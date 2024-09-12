from typing import Callable, TypeVar

import numpy as np
from loguru import logger
from tenacity import retry, wait_random_exponential, stop_after_attempt, RetryCallState

from autoarena.api import api
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.utils import ACCEPTABLE_RESPONSES

JudgeWrapper = Callable[[type[AutomatedJudge]], type[AutomatedJudge]]
T = TypeVar("T", bound=AutomatedJudge)


def ab_shuffling_wrapper(judge_class: type[T]) -> type[T]:
    # not sure why mypy still complains about this after https://github.com/python/mypy/pull/14135
    class ABShufflingJudge(judge_class):  # type: ignore
        """Randomly shuffles which is A and which is B before passing to another judge."""

        def judge(self, h2h: api.HeadToHead) -> str:
            shuffled = np.random.randint(2) == 0
            shuffled_h2h = self._shuffle_h2h(h2h) if shuffled else h2h
            winner = super().judge(shuffled_h2h)
            return self._shuffle_winner(winner) if shuffled else winner

        @staticmethod
        def _shuffle_h2h(h2h: api.HeadToHead) -> api.HeadToHead:
            return api.HeadToHead(
                prompt=h2h.prompt,
                response_a_id=h2h.response_b_id,
                response_a=h2h.response_b,
                response_b_id=h2h.response_a_id,
                response_b=h2h.response_a,
            )

        @staticmethod
        def _shuffle_winner(winner: str) -> str:
            return "B" if winner == "A" else "A" if winner == "B" else "-"

    return ABShufflingJudge


def clean_judgement(winner: str) -> str:
    return winner.strip(" \t\n'\"*.")  # strip common formatting issues


def cleaning_wrapper(judge_class: type[T]) -> type[T]:
    class CleaningJudge(judge_class):  # type: ignore
        """Attempt to clean raw responses from other judges"""

        def judge(self, h2h: api.HeadToHead) -> str:
            winner_raw = super().judge(h2h)
            winner = clean_judgement(winner_raw)
            if winner in ACCEPTABLE_RESPONSES:
                return winner
            else:
                message = f"[{self.__class__.__name__}] Saving bad response from '{self.name}' as tie: {winner_raw}"
                logger.warning(message)
                return "-"

    return CleaningJudge


def fixing_wrapper(judge_class: type[T]) -> type[T]:
    class FixingJudge(judge_class):  # type: ignore
        """If the response does not fit nicely into the expected "A", "B", "-" format, classify it"""

        CLASSIFIER_MODEL = "MoritzLaurer/deberta-v3-xsmall-zeroshot-v1.1-all-33"
        A_IS_BETTER = "A is better"
        B_IS_BETTER = "B is better"
        TIE = "Neither is better / Both are good (Tie)"
        CLASSES = [A_IS_BETTER, B_IS_BETTER, TIE]
        CLASS_TO_WINNER = {A_IS_BETTER: "A", B_IS_BETTER: "B", TIE: "-"}

        def __init__(self, model_name: str, system_prompt: str):
            from transformers import pipeline

            super().__init__(model_name, system_prompt)
            self.pipe = pipeline(model=self.CLASSIFIER_MODEL, device="cpu")

        def judge(self, h2h: api.HeadToHead) -> str:
            winner_raw = super().judge(h2h)
            winner = clean_judgement(winner_raw)
            if winner not in ACCEPTABLE_RESPONSES:
                classifications = self.pipe(winner_raw, candidate_labels=self.CLASSES)
                winner = self.CLASS_TO_WINNER[classifications["labels"][0]]
                logger.warning(f"Fixed bad response: '{winner_raw}' as '{winner}'")
            return winner

    return FixingJudge


def retrying_wrapper(judge_class: type[T]) -> type[T]:
    class RetryingJudge(judge_class):  # type: ignore
        def judge(self, h2h: api.HeadToHead) -> str:
            @retry(wait=wait_random_exponential(min=2, max=10), stop=stop_after_attempt(3), after=self._log_retry)
            def judge_inner(h: api.HeadToHead) -> str:
                return super(RetryingJudge, self).judge(h)

            return judge_inner(h2h)

        def _log_retry(self, retry_state: RetryCallState) -> None:
            message = f"Retrying '{self.name}' attempt {retry_state.attempt_number} (error: {retry_state.outcome})"
            logger.warning(message)

    return RetryingJudge
