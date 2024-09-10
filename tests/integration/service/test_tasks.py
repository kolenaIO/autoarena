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
def models_with_responses(project_slug: str) -> tuple[api.Model, api.Model]:
    df_good_answer = pd.DataFrame.from_records(TEST_QUESTIONS).rename(columns=dict(right="response"))
    model_a = ModelService.upload_responses(project_slug, "good-answers", df_good_answer)
    df_bad_answer = pd.DataFrame.from_records(TEST_QUESTIONS).rename(columns=dict(wrong="response"))
    model_b = ModelService.upload_responses(project_slug, "bad-answers", df_bad_answer)
    return model_a, model_b


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
    models_with_responses: tuple[api.Model, api.Model],
    enabled_auto_judges: tuple[int, int],
) -> None:
    model_a, model_b = models_with_responses
    TaskService.auto_judge(project_slug, [model_a])

    # assert that judging happened as expected
    model_a = ModelService.get_by_id(project_slug, model_a.id)
    model_b = ModelService.get_by_id(project_slug, model_b.id)
    assert model_a.elo > model_b.elo
    assert model_a.n_votes == model_b.n_votes == len(enabled_auto_judges) * len(TEST_QUESTIONS)

    # assert that the task was created and updated
    tasks = TaskService.get_all(project_slug)
    assert len(tasks) == 1
    assert tasks[0].task_type is api.TaskType.AUTO_JUDGE
    assert tasks[0].progress == 1
    assert tasks[0].status is api.TaskStatus.COMPLETED
    assert len(tasks[0].logs) > 0


def test__task__auto_judge__many(
    project_slug: str,
    models_with_responses: tuple[api.Model, api.Model],
    enabled_auto_judges: tuple[int, int],
) -> None:
    model_a, model_b = models_with_responses
    df_good_answer_subset = pd.DataFrame.from_records(TEST_QUESTIONS).rename(columns=dict(right="response")).iloc[:3]
    model_c = ModelService.upload_responses(project_slug, "good-answers-c", df_good_answer_subset)
    TaskService.auto_judge(project_slug, [model_a, model_c])

    model_a = ModelService.get_by_id(project_slug, model_a.id)
    model_b = ModelService.get_by_id(project_slug, model_b.id)
    model_c = ModelService.get_by_id(project_slug, model_c.id)
    n_judges = len(enabled_auto_judges)
    assert model_a.elo > model_c.elo > model_b.elo
    assert model_a.n_votes == model_b.n_votes == n_judges * len(TEST_QUESTIONS) + n_judges * len(df_good_answer_subset)
    assert model_c.n_votes == n_judges * len(df_good_answer_subset) * 2  # compared to both A and B


def test__task__auto_judge__no_head_to_heads(project_slug: str, enabled_auto_judges: tuple[int, int]) -> None:
    df_good_answer = pd.DataFrame.from_records(TEST_QUESTIONS).rename(columns=dict(right="response"))
    model = ModelService.upload_responses(project_slug, "good-answers", df_good_answer)
    TaskService.auto_judge(project_slug, [model])

    # assert that no judging has happened
    assert all(m.n_votes == 0 for m in ModelService.get_all(project_slug))

    # assert that the task was created and makred as completed
    tasks = TaskService.get_all(project_slug)
    assert len(tasks) == 1
    assert tasks[0].task_type is api.TaskType.AUTO_JUDGE
    assert tasks[0].progress == 1
    assert tasks[0].status is api.TaskStatus.COMPLETED
    assert len(tasks[0].logs) > 0


def test__task__recompute_leaderboard(project_slug: str, models_with_responses: tuple[api.Model, api.Model]) -> None:
    model_a, model_b = models_with_responses
    h2hs = HeadToHeadService.get(project_slug, api.HeadToHeadsRequest(model_a_id=model_a.id, model_b_id=model_b.id))
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
