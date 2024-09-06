from autoarena.api import api
from autoarena.judge.custom import CustomJudge


# TODO: remove me, included currently as a demonstration
class AlwaysTieJudge(CustomJudge):
    def judge(self, h2h: api.HeadToHead) -> str:
        print(f"saw: {h2h.prompt}")
        return "-"
