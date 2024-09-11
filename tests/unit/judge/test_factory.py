from datetime import datetime

import pytest

from autoarena.api import api
from autoarena.judge.factory import judge_factory


def test__judge_factory__custom() -> None:
    request = api.Judge(
        id=0,
        judge_type=api.JudgeType.CUSTOM,
        created=datetime.utcnow(),
        name="CustomJudge",
        model_name="abc",
        system_prompt="Always say 'A'",
        description="Example description",
        enabled=True,
        n_votes=0,
    )
    with pytest.raises(NotImplementedError):
        judge_factory(request)
