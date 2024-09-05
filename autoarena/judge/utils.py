import functools
import math
import time
from typing import Callable

import numpy as np
from loguru import logger
from tenacity import retry, RetryCallState
from tenacity import stop_after_attempt
from tenacity import wait_random_exponential

from autoarena.api import api
from autoarena.judge.base import Judge, WrappingJudge

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

# this is more or less a constant as it is baked into the @rate_limit decorators applied to proprietary judges
DEFAULT_BATCH_SIZE = 8


def get_user_prompt(h2h: api.HeadToHead) -> str:
    return USER_PROMPT_TEMPLATE.format(prompt=h2h.prompt, response_a=h2h.response_a, response_b=h2h.response_b)


class ABShufflingJudge(WrappingJudge):
    """Randomly shuffles which is A and which is B before passing to another judge."""

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


class CleaningJudge(WrappingJudge):
    """Attempt to clean raw responses from other judges"""

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        cleaned = []
        for winner_raw in self.judge.judge_batch(batch):
            winner = clean_judgement(winner_raw)
            if winner in ACCEPTABLE_RESPONSES:
                cleaned.append(winner)
            else:
                message = f"[{self.__class__.__name__}] Saving bad response from '{self.name}' as tie: {winner_raw}"
                logger.warning(message)
                cleaned.append("-")
        return cleaned


class FixingJudge(WrappingJudge):
    """If the response does not fit nicely into the expected "A", "B", "-" format, classify it"""

    CLASSIFIER_MODEL = "MoritzLaurer/deberta-v3-xsmall-zeroshot-v1.1-all-33"
    A_IS_BETTER = "A is better"
    B_IS_BETTER = "B is better"
    TIE = "Neither is better / Both are good (Tie)"
    CLASSES = [A_IS_BETTER, B_IS_BETTER, TIE]
    CLASS_TO_WINNER = {A_IS_BETTER: "A", B_IS_BETTER: "B", TIE: "-"}

    def __init__(self, judge: Judge):
        from transformers import pipeline

        super().__init__(judge)
        self.pipe = pipeline(model=self.CLASSIFIER_MODEL, device="cpu")

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        cleaned = []
        for winner_raw in self.judge.judge_batch(batch):
            winner = clean_judgement(winner_raw)
            if winner not in ACCEPTABLE_RESPONSES:
                classifications = self.pipe(winner_raw, candidate_labels=self.CLASSES)
                winner = self.CLASS_TO_WINNER[classifications["labels"][0]]
                logger.warning(f"Fixed bad response: '{winner_raw}' as '{winner}'")
            cleaned.append(winner)
        return cleaned


class RetryingJudge(WrappingJudge):
    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:
        @retry(wait=wait_random_exponential(min=2, max=10), stop=stop_after_attempt(3), after=self._log_retry)
        def judge_batch_inner(b: list[api.HeadToHead]) -> list[str]:
            return self.judge.judge_batch(b)

        return judge_batch_inner(batch)

    def _log_retry(self, retry_state: RetryCallState) -> None:
        message = f"Retrying '{self.judge.name}' attempt {retry_state.attempt_number} (error: {retry_state.outcome})"
        logger.warning(message)


def rate_limit(
    *,
    n_calls: int,
    n_seconds: float,
    n_call_buffer: int = 50,
    max_wait_seconds: float = 60,
    backoff_seconds: float = 1,
) -> Callable:
    call_history: list[float] = []
    assert n_calls - n_call_buffer > 0, f"n_calls ({n_calls}) must be greater than n_call_buffer ({n_call_buffer})"

    def expire_old_calls() -> None:
        nonlocal call_history
        try:
            t_now = time.time()
            expiry_index = next((i for i, call_time in enumerate(call_history) if call_time < t_now - n_seconds))
            call_history = call_history[:expiry_index]
        except StopIteration:
            pass

    def can_call() -> bool:
        return len(call_history) < n_calls - n_call_buffer

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            nonlocal call_history
            expire_old_calls()
            if not can_call():
                logger.warning(f"Hitting rate limit of {n_calls} calls per {n_seconds} seconds, waiting")
            for i in range(math.ceil(max_wait_seconds * backoff_seconds)):
                if not can_call():
                    time.sleep(backoff_seconds)
                expire_old_calls()
                if can_call():
                    break
                if i == max_wait_seconds - 1:
                    logger.error(f"Waited for {max_wait_seconds} seconds and still rate limited, exiting")
                    raise RuntimeError("rate limit exceeded")  # TODO: include name?
            call_history.insert(0, time.time())
            return f(*args, **kwargs)

        return wrapper

    return decorator
