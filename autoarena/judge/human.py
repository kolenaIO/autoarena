from typing import Optional

from autoarena.api import api
from autoarena.api.api import JudgeType
from autoarena.judge.base import Judge


class HumanJudge(Judge):
    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.HUMAN

    @property
    def name(self) -> str:
        return "Human"

    @property
    def model_name(self) -> Optional[str]:
        return None

    @property
    def system_prompt(self) -> Optional[str]:
        return None

    @property
    def description(self) -> str:
        return "Manual ratings submitted via the 'Head-to-Head' tab"

    def judge(self, h2h: api.HeadToHead) -> str:
        raise NotImplementedError
