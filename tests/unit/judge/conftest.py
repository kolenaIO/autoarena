from autoarena.api import api
from autoarena.judge.base import AutomatedJudge


class DummyJudge(AutomatedJudge):
    winners: list[str]

    def __init__(self, model_name: str, system_prompt: str):
        super().__init__(model_name, system_prompt)
        self._name = "DummyJudge"

    def judge(self, h2h: api.HeadToHead) -> str:
        return self.winners.pop(0)

    @classmethod
    def create(cls, winners: list[str], name: str = "DummyJudge") -> "DummyJudge":
        instance = cls("DummyJudge", "could be anything really")
        instance.winners = winners
        instance._name = name
        return instance
