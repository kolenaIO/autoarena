import concurrent
import itertools
from abc import ABCMeta, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Iterator

from autoarena.api import api
from autoarena.judge.base import Judge


class Executor(metaclass=ABCMeta):
    @abstractmethod
    def execute(
        self,
        judges: list[Judge],
        head_to_heads: list[api.HeadToHead],
    ) -> Iterator[tuple[Judge, api.HeadToHead, str]]:
        """Yield responses (winners) from judges as they are ready"""


class BlockingExecutor(Executor):
    def execute(
        self,
        judges: list[Judge],
        head_to_heads: list[api.HeadToHead],
    ) -> Iterator[tuple[Judge, api.HeadToHead, str]]:
        for judge in judges:
            for h2h in head_to_heads:
                yield judge, h2h, judge.judge(h2h)


class ThreadedExecutor(Executor):
    def __init__(self, max_workers: int) -> None:
        self.pool = ThreadPoolExecutor(max_workers=max_workers)

    def execute(
        self,
        judges: list[Judge],
        head_to_heads: list[api.HeadToHead],
    ) -> Iterator[tuple[Judge, api.HeadToHead, str]]:
        h2h_with_judges = list(itertools.product(head_to_heads, judges))

        def run(h2h_with_judge: tuple[api.HeadToHead, Judge]) -> tuple[Judge, api.HeadToHead, str]:
            h, j = h2h_with_judge
            return j, h, j.judge(h)

        futures = [self.pool.submit(run, h2h_w_j) for h2h_w_j in h2h_with_judges]
        for future in concurrent.futures.as_completed(futures):
            judge, h2h, winner = future.result()
            yield judge, h2h, winner
