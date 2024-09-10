import pandas as pd
import pytest

from autoarena.api import api
from autoarena.service.head_to_head import HeadToHeadService
from autoarena.service.judge import JudgeService
from autoarena.service.model import ModelService
from autoarena.service.task import TaskService
from tests.integration.judge.conftest import TEST_JUDGE_MODEL_NAMES

TEST_QUESTIONS = [
    dict(prompt="What is 2+2?", wrong="100 million", right="4"),
    dict(prompt="Is Python 2 still supported?", wrong="Of course", right="Not by PSF"),
    dict(prompt="What country shares the longest land border with the USA?", wrong="Jamaica", right="Canada"),
    dict(prompt="Who directed Fantastic Mr. Fox?", wrong="Christopher Nolan", right="Wes Anderson"),
    dict(prompt="Does the Earth orbit the Sun?", wrong="Of course not", right="Yes"),
]


@pytest.fixture
def model_ids_with_responses(project_slug: str) -> tuple[int, int]:
    df_good_answer = pd.DataFrame.from_records(TEST_QUESTIONS).rename(columns=dict(right="response"))
    model_a_id = ModelService.upload_responses(project_slug, "good-answers", df_good_answer).id
    df_bad_answer = pd.DataFrame.from_records(TEST_QUESTIONS).rename(columns=dict(wrong="response"))
    model_b_id = ModelService.upload_responses(project_slug, "bad-answers", df_bad_answer).id
    return model_a_id, model_b_id


@pytest.fixture
def enabled_auto_judges(project_slug: str) -> tuple[int, int]:
    # should be enabled by default
    judge_a_id = JudgeService.create(project_slug, create_judge_request(api.JudgeType.OPENAI)).id
    judge_b_id = JudgeService.create(project_slug, create_judge_request(api.JudgeType.COHERE)).id
    return judge_a_id, judge_b_id


def create_judge_request(judge_type: api.JudgeType) -> api.CreateJudgeRequest:
    return api.CreateJudgeRequest(
        judge_type=judge_type,
        name=TEST_JUDGE_MODEL_NAMES[judge_type],
        model_name=TEST_JUDGE_MODEL_NAMES[judge_type],
        system_prompt=JudgeService.get_default_system_prompt(),
        description="Just for testing",
    )


# test here rather than via API as synchronous autojudging is not exposed via the API
def test__task__auto_judge(
    project_slug: str,
    model_ids_with_responses: tuple[int, int],
    enabled_auto_judges: tuple[int, int],
) -> None:
    model_a_id, model_b_id = model_ids_with_responses
    TaskService.auto_judge(project_slug, model_a_id, "good-answers")

    # assert that judging happened as expected
    models = ModelService.get_all(project_slug)
    model_a = [m for m in models if m.id == model_a_id][0]
    model_b = [m for m in models if m.id == model_b_id][0]
    assert model_a.elo > model_b.elo
    assert model_a.n_votes == 2 * len(TEST_QUESTIONS)
    assert model_b.n_votes == 2 * len(TEST_QUESTIONS)

    # assert that the task was created and updated
    tasks = TaskService.get_all(project_slug)
    assert len(tasks) == 1
    assert tasks[0].task_type is api.TaskType.AUTO_JUDGE
    assert tasks[0].progress == 1
    assert tasks[0].status is api.TaskStatus.COMPLETED
    assert len(tasks[0].logs) > 0


def test__task__auto_judge__no_head_to_heads(project_slug: str, enabled_auto_judges: tuple[int, int]) -> None:
    df_good_answer = pd.DataFrame.from_records(TEST_QUESTIONS).rename(columns=dict(right="response"))
    model_id = ModelService.upload_responses(project_slug, "good-answers", df_good_answer).id
    TaskService.auto_judge(project_slug, model_id, "good-answers")

    # assert that no judging has happened
    assert all(m.n_votes == 0 for m in ModelService.get_all(project_slug))

    # assert that the task was created and makred as completed
    tasks = TaskService.get_all(project_slug)
    assert len(tasks) == 1
    assert tasks[0].task_type is api.TaskType.AUTO_JUDGE
    assert tasks[0].progress == 1
    assert tasks[0].status is api.TaskStatus.COMPLETED
    assert len(tasks[0].logs) > 0


def test__task__recompute_leaderboard(project_slug: str, model_ids_with_responses: tuple[int, int]) -> None:
    model_a_id, model_b_id = model_ids_with_responses
    h2hs = HeadToHeadService.get(project_slug, api.HeadToHeadsRequest(model_a_id=model_a_id, model_b_id=model_b_id))
    for h2h in h2hs:
        vote = api.HeadToHeadVoteRequest(response_a_id=h2h.response_a_id, response_b_id=h2h.response_b_id, winner="A")
        HeadToHeadService.submit_vote(project_slug, vote)
    models_before = ModelService.get_all(project_slug)
    TaskService.recompute_leaderboard(project_slug)
    models_after = ModelService.get_all(project_slug)

    # assert that recomputation reproduced the same scores as the step-by-step from sequential judgements
    assert all(before.elo == after.elo for before, after in zip(models_before, models_after))
    assert all(before.n_votes == after.n_votes == len(h2hs) for before, after in zip(models_before, models_after))

    # assert that the task was created and updated
    tasks = TaskService.get_all(project_slug)
    assert len(tasks) == 1
    assert tasks[0].task_type is api.TaskType.RECOMPUTE_LEADERBOARD
    assert tasks[0].progress == 1
    assert len(tasks[0].status) > 0
