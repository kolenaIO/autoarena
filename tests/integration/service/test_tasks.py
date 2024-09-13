import pandas as pd
import pytest

from autoarena.api import api
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.custom import register_custom_judge_class
from autoarena.service.head_to_head import HeadToHeadService
from autoarena.service.judge import JudgeService
from autoarena.service.model import ModelService
from autoarena.service.task import TaskService

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
def enabled_auto_judges(project_slug: str) -> list[int]:
    class VotesForTheGoodOneJudge(AutomatedJudge):
        def judge(self, prompt: str, response_a: str, response_b: str) -> str:
            good_answers = set(q["right"] for q in TEST_QUESTIONS)
            a_good = response_a in good_answers
            b_good = response_b in good_answers
            return "A" if a_good and not b_good else "B" if b_good else "-"

    register_custom_judge_class("GoodJudge1", VotesForTheGoodOneJudge)
    register_custom_judge_class("GoodJudge2", VotesForTheGoodOneJudge)
    register_custom_judge_class("GoodJudge3", VotesForTheGoodOneJudge)
    # should be enabled by default
    judge_a_id = JudgeService.create(project_slug, create_custom_judge_request("GoodJudge1")).id
    judge_b_id = JudgeService.create(project_slug, create_custom_judge_request("GoodJudge2")).id
    judge_c_id = JudgeService.create(project_slug, create_custom_judge_request("GoodJudge3")).id
    return [judge_a_id, judge_b_id, judge_c_id]


def create_custom_judge_request(name: str) -> api.CreateJudgeRequest:
    return api.CreateJudgeRequest(
        judge_type=api.JudgeType.CUSTOM,
        name=name,
        model_name=name,
        system_prompt="doesn't matter",
        description="Just for testing",
    )


# test here rather than via API as synchronous autojudging is not exposed via the API
def test__task__auto_judge_by_models(
    project_slug: str,
    models_with_responses: tuple[api.Model, api.Model],
    enabled_auto_judges: list[int],
) -> None:
    model_a, model_b = models_with_responses
    TaskService.auto_judge_by_models(project_slug, [model_a])

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


def test__task__auto_judge_by_models__many(
    project_slug: str,
    models_with_responses: tuple[api.Model, api.Model],
    enabled_auto_judges: list[int],
) -> None:
    model_a, model_b = models_with_responses
    df_good_answer_subset = pd.DataFrame.from_records(TEST_QUESTIONS).rename(columns=dict(right="response")).iloc[:2]
    df_bad_answer_subset = pd.DataFrame.from_records(TEST_QUESTIONS).rename(columns=dict(wrong="response")).iloc[3:]
    df_c = pd.concat([df_good_answer_subset, df_bad_answer_subset])
    model_c = ModelService.upload_responses(project_slug, "good-answers-c", df_c)
    TaskService.auto_judge_by_models(project_slug, [model_a, model_c])

    model_a = ModelService.get_by_id(project_slug, model_a.id)
    model_b = ModelService.get_by_id(project_slug, model_b.id)
    model_c = ModelService.get_by_id(project_slug, model_c.id)
    n_judges = len(enabled_auto_judges)
    assert model_a.elo > model_c.elo > model_b.elo
    assert model_a.n_votes == model_b.n_votes == n_judges * len(TEST_QUESTIONS) + n_judges * len(df_c)
    assert model_c.n_votes == n_judges * len(df_c) * 2  # compared to both A and B


def test__task__auto_judge_by_models__no_head_to_heads(project_slug: str, enabled_auto_judges: list[int]) -> None:
    df_good_answer = pd.DataFrame.from_records(TEST_QUESTIONS).rename(columns=dict(right="response"))
    model = ModelService.upload_responses(project_slug, "good-answers", df_good_answer)
    TaskService.auto_judge_by_models(project_slug, [model])

    # assert that no judging has happened
    assert all(m.n_votes == 0 for m in ModelService.get_all(project_slug))

    # assert that the task was created and marked as completed
    tasks = TaskService.get_all(project_slug)
    assert len(tasks) == 1
    assert tasks[0].task_type is api.TaskType.AUTO_JUDGE
    assert tasks[0].progress == 1
    assert tasks[0].status is api.TaskStatus.COMPLETED
    assert len(tasks[0].logs) > 0


def test__task__auto_judge_by_judges(
    project_slug: str,
    models_with_responses: tuple[api.Model, api.Model],
    enabled_auto_judges: list[int],
) -> None:
    judges = [j for j in JudgeService.get_all(project_slug) if j.id in enabled_auto_judges]

    # check that fraction is applied correctly
    TaskService.auto_judge_by_judges(project_slug, judges, fraction=0.6)
    judges = [j for j in JudgeService.get_all(project_slug) if j.id in enabled_auto_judges]
    assert all(j.n_votes == int(0.6 * len(TEST_QUESTIONS)) for j in judges)

    # check that skip_existing is applied correctly
    TaskService.auto_judge_by_judges(project_slug, judges, skip_existing=True)
    judges = [j for j in JudgeService.get_all(project_slug) if j.id in enabled_auto_judges]
    assert all(j.n_votes == len(TEST_QUESTIONS) for j in judges)

    # check that skip_existing is idempotent
    TaskService.auto_judge_by_judges(project_slug, judges, skip_existing=True)
    judges = [j for j in JudgeService.get_all(project_slug) if j.id in enabled_auto_judges]
    assert all(j.n_votes == len(TEST_QUESTIONS) for j in judges)


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
