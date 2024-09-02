import itertools
from abc import ABCMeta, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Iterator

import numpy as np

from autostack.api import api
from autostack.judge.base import Judge


class Executor(metaclass=ABCMeta):
    @abstractmethod
    def execute(
        self,
        judges: list[Judge],
        head_to_heads: list[api.HeadToHead],
        batch_size: int = 8,
    ) -> Iterator[tuple[Judge, list[str]]]:
        """Yield batches from judges as they are ready"""


class BlockingExecutor(Executor):
    def execute(
        self,
        judges: list[Judge],
        head_to_heads: list[api.HeadToHead],
        batch_size: int = 8,
    ) -> Iterator[tuple[Judge, list[str]]]:
        n_batches = len(head_to_heads) // batch_size
        for judge in judges:
            for batch in np.array_split(head_to_heads, n_batches):
                yield judge, judge.judge_batch(batch)


class ThreadedExecutor(Executor):
    def __init__(self, max_workers: int) -> None:
        self.pool = ThreadPoolExecutor(max_workers=max_workers)

    def execute(
        self,
        judges: list[Judge],
        head_to_heads: list[api.HeadToHead],
        batch_size: int = 8,
    ) -> Iterator[tuple[Judge, list[str]]]:
        n_batches = len(head_to_heads) // batch_size
        batches = np.array_split(head_to_heads, n_batches)
        batches_with_judges = list(itertools.product(batches, judges))

        def run_judge(batch_with_judge: tuple[list[api.HeadToHead], Judge]) -> tuple[Judge, list[str]]:
            batch, j = batch_with_judge
            return j, j.judge_batch(batch)

        for judge, processed_batch in self.pool.map(run_judge, batches_with_judges):
            yield judge, processed_batch
