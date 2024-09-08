# test here rather than via API as synchronous autojudging is not exposed via the API
import pandas as pd

from autoarena.api import api
from autoarena.service.judge import JudgeService
from autoarena.service.model import ModelService
from autoarena.service.project import ProjectService
from autoarena.service.task import TaskService
from tests.integration.judge.conftest import TEST_JUDGE_MODEL_NAMES

DF_BAD_ANSWER = pd.DataFrame.from_records(
    [
        dict(prompt="What is 2+2?", response="100 million"),
        dict(prompt="Is Python 2 still supported?", response="Of course"),
        dict(prompt="What country shares the longest land border with the USA?", response="Jamaica"),
        dict(prompt="Who directed Fantastic Mr. Fox?", response="Christopher Nolan"),
        dict(prompt="Does the Earth orbit the Sun?", response="Of course not"),
    ]
)

DF_GOOD_ANSWER = pd.DataFrame.from_records(
    [
        dict(prompt="What is 2+2?", response="4"),
        dict(prompt="Is Python 2 still supported?", response="Not by PSF"),
        dict(prompt="What country shares the longest land border with the USA?", response="Canada"),
        dict(prompt="Who directed Fantastic Mr. Fox?", response="Wes Anderson"),
        dict(prompt="Does the Earth orbit the Sun?", response="Yes"),
    ]
)


def test__task__auto_judge(with_empty_database: None) -> None:
    project_id = ProjectService.create_idempotent(api.CreateProjectRequest(name="test__task__auto_judge")).id
    create_judge_request = api.CreateJudgeRequest(
        project_id=project_id,
        judge_type=api.JudgeType.OPENAI,
        name=TEST_JUDGE_MODEL_NAMES[api.JudgeType.OPENAI],
        model_name=TEST_JUDGE_MODEL_NAMES[api.JudgeType.OPENAI],
        system_prompt=JudgeService.get_default_system_prompt(),
        description="Just for testing",
    )
    JudgeService.create(create_judge_request)  # should be enabled by default
    model_a_id = ModelService.upload_results(project_id, "good-answers", DF_GOOD_ANSWER).id
    model_b_id = ModelService.upload_results(project_id, "bad-answers", DF_BAD_ANSWER).id
    TaskService.auto_judge(project_id, model_a_id, "good-answers")
    models = ModelService.get_all(project_id)
    model_a = [m for m in models if m.id == model_a_id][0]
    model_b = [m for m in models if m.id == model_b_id][0]
    assert model_a.elo > model_b.elo
    assert model_a.votes == len(DF_GOOD_ANSWER)
    assert model_b.votes == len(DF_GOOD_ANSWER)
