import functools
import math
import sys
import time
from typing import Callable

if sys.version_info[:2] >= (3, 10):
    from typing import ParamSpec, TypeVar
else:
    from typing_extensions import ParamSpec, TypeVar

from loguru import logger


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


def get_user_prompt(prompt: str, response_a: str, response_b: str) -> str:
    return USER_PROMPT_TEMPLATE.format(prompt=prompt, response_a=response_a, response_b=response_b)


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

    Params = ParamSpec("Params")
    ReturnType = TypeVar("ReturnType")

    def decorator(f: Callable[Params, ReturnType]) -> Callable[Params, ReturnType]:
        @functools.wraps(f)
        def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> ReturnType:
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
