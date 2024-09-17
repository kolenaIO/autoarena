from typing import TypeVar

from autoarena.judge.base import AutomatedJudge

T = TypeVar("T", bound="DummyJudge")


class DummyJudge(AutomatedJudge):
    winners: list[str]

    def judge(self, prompt: str, response_a: str, response_b: str) -> str:
        return self.winners.pop(0)

    @classmethod
    def create(cls: type[T], winners: list[str]) -> T:
        instance = cls("DummyJudge", "DummyJudge", "could be anything really")
        instance.winners = [*winners]
        return instance
