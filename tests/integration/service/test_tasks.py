import contextvars
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional

import pandas as pd
import pytest

from autoarena.api import api
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.custom import register_custom_judge_class
from autoarena.judge.executor import BlockingExecutor
from autoarena.service.head_to_head import HeadToHeadService
from autoarena.service.judge import JudgeService
from autoarena.service.model import ModelService
from autoarena.service.task import TaskService
from autoarena.store.environment import KeyManager
from autoarena.task.auto_judge import AutoJudgeTask

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
def enabled_auto_judges(project_slug: str) -> list[api.Judge]:
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
    return [
        JudgeService.create(project_slug, create_custom_judge_request("GoodJudge1")),
        JudgeService.create(project_slug, create_custom_judge_request("GoodJudge2")),
        JudgeService.create(project_slug, create_custom_judge_request("GoodJudge3")),
    ]


def create_custom_judge_request(name: str) -> api.CreateJudgeRequest:
    return api.CreateJudgeRequest(
        judge_type=api.JudgeType.CUSTOM,
        name=name,
        model_name=name,
        system_prompt="doesn't matter",
        description="Just for testing",
    )


# test here rather than via API as synchronous autojudging is not exposed via the API
def test__task__auto_judge__models(
    project_slug: str,
    models_with_responses: tuple[api.Model, api.Model],
    enabled_auto_judges: list[api.Judge],
) -> None:
    model_a, model_b = models_with_responses
    TaskService.auto_judge(project_slug, models=[model_a])

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
    enabled_auto_judges: list[api.Judge],
) -> None:
    model_a, model_b = models_with_responses
    df_good_answer_subset = pd.DataFrame.from_records(TEST_QUESTIONS).rename(columns=dict(right="response")).iloc[:2]
    df_bad_answer_subset = pd.DataFrame.from_records(TEST_QUESTIONS).rename(columns=dict(wrong="response")).iloc[3:]
    df_c = pd.concat([df_good_answer_subset, df_bad_answer_subset])
    model_c = ModelService.upload_responses(project_slug, "good-answers-c", df_c)
    TaskService.auto_judge(project_slug, models=[model_a, model_c])

    model_a = ModelService.get_by_id(project_slug, model_a.id)
    model_b = ModelService.get_by_id(project_slug, model_b.id)
    model_c = ModelService.get_by_id(project_slug, model_c.id)
    n_judges = len(enabled_auto_judges)
    assert model_a.elo > model_c.elo > model_b.elo
    assert model_a.n_votes == model_b.n_votes == n_judges * len(TEST_QUESTIONS) + n_judges * len(df_c)
    assert model_c.n_votes == n_judges * len(df_c) * 2  # compared to both A and B


def test__task__auto_judge__no_head_to_heads(project_slug: str, enabled_auto_judges: list[int]) -> None:
    df_good_answer = pd.DataFrame.from_records(TEST_QUESTIONS).rename(columns=dict(right="response"))
    model = ModelService.upload_responses(project_slug, "good-answers", df_good_answer)
    TaskService.auto_judge(project_slug, models=[model])

    # assert that no judging has happened
    assert all(m.n_votes == 0 for m in ModelService.get_all(project_slug))

    # assert that the task was created and marked as completed
    tasks = TaskService.get_all(project_slug)
    assert len(tasks) == 1
    assert tasks[0].task_type is api.TaskType.AUTO_JUDGE
    assert tasks[0].progress == 1
    assert tasks[0].status is api.TaskStatus.COMPLETED
    assert len(tasks[0].logs) > 0


def test__task__auto_judge__no_enabled_judges(
    project_slug: str,
    models_with_responses: tuple[api.Model, api.Model],
    log_stream: Callable[[], str],
) -> None:
    TaskService.auto_judge(project_slug, models=list(models_with_responses))
    assert "No enabled judges found" in log_stream()


def test__task__auto_judge__judges(
    project_slug: str,
    models_with_responses: tuple[api.Model, api.Model],
    enabled_auto_judges: list[api.Judge],
) -> None:
    enabled_auto_judge_ids = {j.id for j in enabled_auto_judges}
    # check that fraction is applied correctly
    TaskService.auto_judge(project_slug, judges=enabled_auto_judges, fraction=0.6)
    judges = [j for j in JudgeService.get_all(project_slug) if j.id in enabled_auto_judge_ids]
    assert all(j.n_votes == int(0.6 * len(TEST_QUESTIONS)) for j in judges)

    # check that skip_existing is applied correctly
    for _ in range(2):  # loop to check idempotence
        TaskService.auto_judge(project_slug, judges=judges, skip_existing=True)
        judges = [j for j in JudgeService.get_all(project_slug) if j.id in enabled_auto_judge_ids]
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


def test__auto_judge_task__saves_progress(
    project_slug: str,
    models_with_responses: tuple[api.Model, api.Model],
    enabled_auto_judges: list[api.Judge],
    log_stream: Callable[[], str],
) -> None:
    class CrashesAfter3Judge(AutomatedJudge):
        def __init__(self, name: str, model_name: str, system_prompt: str, key_manager: Optional[KeyManager] = None):
            super().__init__(name, model_name, system_prompt, key_manager=key_manager)
            self.seen = 0

        def judge(self, prompt: str, response_a: str, response_b: str) -> str:
            self.seen += 1
            if self.seen > 3:
                raise RuntimeError(f"seen {self.seen}")
            return "-"

    register_custom_judge_class(CrashesAfter3Judge.__name__, CrashesAfter3Judge)
    crashing_judge = JudgeService.create(project_slug, create_custom_judge_request(CrashesAfter3Judge.__name__))

    task_id = TaskService.create(project_slug, api.TaskType.AUTO_JUDGE).id
    auto_judge_task = AutoJudgeTask(
        project_slug=project_slug,
        task_id=task_id,
        models=list(models_with_responses),
        judges=[*enabled_auto_judges, crashing_judge],
        judge_wrappers=[],
        update_every=2,
    )

    with pytest.raises(RuntimeError):
        with BlockingExecutor() as executor:
            auto_judge_task.run(executor)

    assert "ERROR" in log_stream() and "seen 4" in log_stream()
    tasks = TaskService.get_all(project_slug)
    assert len(tasks) == 1
    assert tasks[0].status == api.TaskStatus.FAILED
    enabled_auto_judge_ids = {j.id for j in enabled_auto_judges}
    judges = [j for j in JudgeService.get_all(project_slug) if j.id in enabled_auto_judge_ids | {crashing_judge.id}]
    assert len(judges) == 4
    assert all([j.n_votes == len(TEST_QUESTIONS) for j in judges if j in enabled_auto_judge_ids])  # saved
    crashing_judge = [j for j in judges if j.id == crashing_judge.id][0]
    assert crashing_judge.n_votes == 2  # crashed on 4, saved first 2


@pytest.mark.parametrize("n_tasks", [2, 4, 8])
def test__auto_judge_task__saves_progress__concurrent(
    project_slug: str,
    models_with_responses: tuple[api.Model, api.Model],
    enabled_auto_judges: list[api.Judge],
    log_stream: Callable[[], str],
    n_tasks: int,
) -> None:
    tasks = []
    for _ in range(n_tasks):
        task_id = TaskService.create(project_slug, api.TaskType.AUTO_JUDGE).id
        auto_judge_task = AutoJudgeTask(
            project_slug=project_slug,
            task_id=task_id,
            models=list(models_with_responses),
            judges=enabled_auto_judges,
            judge_wrappers=[],
            update_every=1,
        )
        tasks.append(auto_judge_task)

    with ThreadPoolExecutor(max_workers=n_tasks) as executor:
        # ensure that each task is running with the same context by copying it in
        futures = [executor.submit(contextvars.copy_context().run, t.run, BlockingExecutor()) for t in tasks]

    assert all(f.result() is None for f in futures)
    assert log_stream().count("SUCCESS") == n_tasks
    task_ids = {t.task_id for t in tasks}
    assert all(t.status is api.TaskStatus.COMPLETED for t in TaskService.get_all(project_slug) if t.id in task_ids)
    enabled_auto_judge_ids = {j.id for j in enabled_auto_judges}
    judges = [j for j in JudgeService.get_all(project_slug) if j.id in enabled_auto_judge_ids]
    assert len(judges) == len(enabled_auto_judges)
    assert all([j.n_votes == len(TEST_QUESTIONS) for j in judges])
