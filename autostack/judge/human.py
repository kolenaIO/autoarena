from autostack.api import api
from autostack.api.api import JudgeType
from autostack.judge.base import Judge


class HumanJudge(Judge):
    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.HUMAN

    @property
    def name(self) -> str:
        return "Human"

    @property
    def description(self) -> str:
        return "Manual ratings submitted via the 'Head-to-Head' tab"

    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:  # TODO: return more information than just winner?
        raise NotImplementedError
