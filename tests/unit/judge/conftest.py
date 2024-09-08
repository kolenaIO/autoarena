from typing import Optional

from autoarena.api import api
from autoarena.api.api import JudgeType
from autoarena.judge.base import Judge


class DummyJudge(Judge):
    def __init__(self, winners: list[str], name: str = "DummyJudge"):
        self._winners = [*winners]
        self._name = name

    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.CUSTOM

    @property
    def name(self) -> str:
        return self._name

    @property
    def model_name(self) -> Optional[str]:
        return None

    @property
    def system_prompt(self) -> Optional[str]:
        return None

    @property
    def description(self) -> str:
        return "judge for testing"

    def judge(self, h2h: api.HeadToHead) -> str:
        return self._winners.pop(0)
