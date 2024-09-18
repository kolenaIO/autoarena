import concurrent
import random
from abc import ABCMeta, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from types import TracebackType
from typing import Iterator, TypeVar, Optional

from autoarena.api import api
from autoarena.judge.base import AutomatedJudge

T = TypeVar("T", bound="JudgeExecutor")


class JudgeExecutor(metaclass=ABCMeta):
    def __enter__(self: T) -> T:
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None: ...

    @abstractmethod
    def execute(
        self, judges_with_head_to_heads: list[tuple[AutomatedJudge, list[api.HeadToHead]]]
    ) -> Iterator[tuple[AutomatedJudge, api.HeadToHead, str]]:
        """Yield responses (winners) from judges as they are ready"""


class BlockingExecutor(JudgeExecutor):
    def execute(
        self, judges_with_head_to_heads: list[tuple[AutomatedJudge, list[api.HeadToHead]]]
    ) -> Iterator[tuple[AutomatedJudge, api.HeadToHead, str]]:
        for judge, head_to_heads in judges_with_head_to_heads:
            for h2h in head_to_heads:
                yield judge, h2h, judge.judge(h2h.prompt, h2h.response_a, h2h.response_b)


class ThreadedExecutor(JudgeExecutor):
    def __init__(self, max_workers: int) -> None:
        self.pool = ThreadPoolExecutor(max_workers=max_workers)

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.pool.shutdown(wait=False, cancel_futures=True)

    def execute(
        self, judges_with_head_to_heads: list[tuple[AutomatedJudge, list[api.HeadToHead]]]
    ) -> Iterator[tuple[AutomatedJudge, api.HeadToHead, str]]:
        h2h_with_judges = [(h2h, judge) for judge, h2hs in judges_with_head_to_heads for h2h in h2hs]
        random.shuffle(h2h_with_judges)  # ensure that we are running all judges concurrently to best load balance

        def run(h2h_with_judge: tuple[api.HeadToHead, AutomatedJudge]) -> tuple[AutomatedJudge, api.HeadToHead, str]:
            h, j = h2h_with_judge
            return j, h, j.judge(h.prompt, h.response_a, h.response_b)

        futures = [self.pool.submit(run, h2h_w_j) for h2h_w_j in h2h_with_judges]
        for future in concurrent.futures.as_completed(futures):
            judge, h2h, winner = future.result()
            yield judge, h2h, winner
