from collections import defaultdict

from autoarena.api import api
from autoarena.judge.executor import BlockingExecutor, ThreadedExecutor
from tests.unit.judge.conftest import DummyJudge

DUMMY_WINNERS = ["A", "B", "-"] * 50
DUMMY_H2HS = [
    api.HeadToHead(
        result_a=api.Result(id=100 + i, prompt=f"prompt: {i}", response=f"response A: {i}"),
        result_b=api.Result(id=200 + i, prompt=f"prompt: {i}", response=f"response B: {i}"),
    )
    for i in range(len(DUMMY_WINNERS))
]


def test__blocking_executor() -> None:
    judge1 = DummyJudge(DUMMY_WINNERS)
    judge2 = DummyJudge(["-"] * len(DUMMY_WINNERS))
    executor = BlockingExecutor()
    out = list(executor.execute([judge1, judge2], DUMMY_H2HS))
    expected1 = [(judge1, h2h, w) for h2h, w in zip(DUMMY_H2HS, DUMMY_WINNERS)]
    expected2 = [(judge2, h2h, "-") for h2h in DUMMY_H2HS]
    assert out == [*expected1, *expected2]


def test__threaded_executor() -> None:
    judge1 = DummyJudge(DUMMY_WINNERS, name="DummyJudge1")
    judge2 = DummyJudge(["-"] * len(DUMMY_WINNERS), name="DummyJudge2")
    executor = ThreadedExecutor(4)
    winner_by_judge_name: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    for judge, h2h, winner in executor.execute([judge1, judge2], DUMMY_H2HS):
        existing = winner_by_judge_name[judge.name]
        tup = (h2h.result_a.id, h2h.result_b.id, winner)
        winner_by_judge_name[judge.name] = sorted([*existing, tup], key=lambda t: t[0])
    assert [w for _, _, w in winner_by_judge_name[judge1.name]] == DUMMY_WINNERS
    assert [w for _, _, w in winner_by_judge_name[judge2.name]] == ["-"] * len(DUMMY_WINNERS)
