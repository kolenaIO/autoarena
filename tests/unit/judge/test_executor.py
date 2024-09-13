from collections import defaultdict

import numpy as np

from autoarena.api import api
from autoarena.judge.executor import BlockingExecutor, ThreadedExecutor
from tests.unit.judge.conftest import DummyJudge

DUMMY_WINNERS = ["A", "B", "-"] * 50
DUMMY_H2HS = [
    api.HeadToHead(
        prompt=f"prompt: {i}",
        response_a_id=100 + i,
        response_b_id=200 + i,
        response_a=f"response A: {i}",
        response_b=f"response b: {i}",
    )
    for i in range(len(DUMMY_WINNERS))
]


def test__blocking_executor() -> None:
    judge1 = DummyJudge.create(DUMMY_WINNERS)
    judge2 = DummyJudge.create(["-"] * len(DUMMY_WINNERS))
    with BlockingExecutor() as executor:
        out = list(executor.execute([(judge1, DUMMY_H2HS), (judge2, DUMMY_H2HS)]))
    expected1 = [(judge1, h2h, w) for h2h, w in zip(DUMMY_H2HS, DUMMY_WINNERS)]
    expected2 = [(judge2, h2h, "-") for h2h in DUMMY_H2HS]
    assert out == [*expected1, *expected2]


def test__threaded_executor() -> None:
    judge1 = DummyJudge.create(DUMMY_WINNERS)
    judge2 = DummyJudge.create(["-"] * len(DUMMY_WINNERS))
    winner_by_judge: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
    with ThreadedExecutor(8) as executor:
        for judge, h2h, winner in executor.execute([(judge1, DUMMY_H2HS), (judge2, DUMMY_H2HS)]):
            winner_by_judge[id(judge)].append((h2h.response_a_id, h2h.response_b_id, winner))
    winner_arr = np.array([w for _, _, w in winner_by_judge[id(judge1)]])
    assert sum(winner_arr == "A") == sum(winner_arr == "B") == sum(winner_arr == "-")  # may have been seen in any order
    assert [w for _, _, w in winner_by_judge[id(judge2)]] == ["-"] * len(DUMMY_WINNERS)
