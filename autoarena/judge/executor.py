import concurrent
import itertools
from abc import ABCMeta, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Iterator

import numpy as np

from autoarena.api import api
from autoarena.judge.base import Judge
from autoarena.judge.utils import DEFAULT_BATCH_SIZE


# TODO: this interface is a little gnarly as callers need to deal with responses coming back in any order
class Executor(metaclass=ABCMeta):
    @abstractmethod
    def execute(
        self,
        judges: list[Judge],
        head_to_heads: list[api.HeadToHead],
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> Iterator[tuple[Judge, list[api.HeadToHead], list[str]]]:
        """Yield batches from judges as they are ready"""


class BlockingExecutor(Executor):
    def execute(
        self,
        judges: list[Judge],
        head_to_heads: list[api.HeadToHead],
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> Iterator[tuple[Judge, list[api.HeadToHead], list[str]]]:
        n_batches = len(head_to_heads) // batch_size
        for judge in judges:
            for batch in np.array_split(head_to_heads, n_batches):
                yield judge, batch, judge.judge_batch(batch)


class ThreadedExecutor(Executor):
    def __init__(self, max_workers: int) -> None:
        self.pool = ThreadPoolExecutor(max_workers=max_workers)

    def execute(
        self,
        judges: list[Judge],
        head_to_heads: list[api.HeadToHead],
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> Iterator[tuple[Judge, list[api.HeadToHead], list[str]]]:
        n_batches = max(len(head_to_heads) // batch_size, 1)
        batches = [b for b in np.array_split(head_to_heads, n_batches) if len(b) > 0]
        batches_with_judges = list(itertools.product(batches, judges))

        def run(batch_with_judge: tuple[list[api.HeadToHead], Judge]) -> tuple[Judge, list[api.HeadToHead], list[str]]:
            b, j = batch_with_judge
            return j, b, j.judge_batch(b)

        futures = [self.pool.submit(run, bwj) for bwj in batches_with_judges]
        for future in concurrent.futures.as_completed(futures):
            judge, batch, judged_batch = future.result()
            yield judge, batch, judged_batch
