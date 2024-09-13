import time
from collections import defaultdict
from datetime import datetime
from typing import Optional

import pandas as pd
from loguru import logger

from autoarena.api import api
from autoarena.api.api import JudgeType
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.executor import ThreadedExecutor, JudgeExecutor
from autoarena.judge.factory import judge_factory
from autoarena.judge.wrapper import ab_shuffling_wrapper, fixing_wrapper, retrying_wrapper
from autoarena.service.elo import EloService
from autoarena.service.head_to_head import HeadToHeadService
from autoarena.service.judge import JudgeService
from autoarena.service.model import ModelService
from autoarena.service.project import ProjectService
from autoarena.store.utils import id_slug


class TaskService:
    @staticmethod
    def get_all(project_slug: str) -> list[api.Task]:
        with ProjectService.connect(project_slug) as conn:
            df_task = conn.execute("SELECT id, task_type, created, progress, status, logs FROM task").df()
        return [api.Task(**r) for _, r in df_task.iterrows()]

    @staticmethod
    def create(project_slug: str, task_type: api.TaskType, log: str = "Started") -> api.Task:
        with ProjectService.connect(project_slug) as conn:
            logs = f"{TaskService._time_slug()} {log}"
            ((task_id, created, progress, status, logs),) = conn.execute(
                """
                INSERT INTO task (task_type, status, logs)
                VALUES ($task_type, $status, $logs)
                RETURNING id, created, progress, status, logs
                """,
                dict(task_type=task_type.value, status=api.TaskStatus.STARTED.value, logs=logs),
            ).fetchall()
        return api.Task(id=task_id, task_type=task_type, created=created, progress=progress, status=status, logs=logs)

    @staticmethod
    def delete_completed(project_slug: str) -> None:
        with ProjectService.connect(project_slug) as conn:
            conn.execute("TRUNCATE task")

    @staticmethod
    def _time_slug() -> str:
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    # TODO: should this really be a long-running task? It only takes ~5 seconds for ~50k head-to-heads
    @staticmethod
    def recompute_leaderboard(project_slug: str) -> None:
        task_objects = TaskService.get_all(project_slug)
        if len([t for t in task_objects if t.task_type is api.TaskType.RECOMPUTE_LEADERBOARD and t.progress < 1]) > 0:
            return  # only recompute if there isn't already a task in progress
        api_task = TaskService.create(project_slug, api.TaskType.RECOMPUTE_LEADERBOARD)
        task = TaskService.Task(project_slug, api_task)
        try:
            EloService.reseed_scores(project_slug)
        finally:
            task.update("Done", progress=1, status=api.TaskStatus.COMPLETED)

    @staticmethod
    def auto_judge_by_judges(
        project_slug: str,
        judges: list[api.Judge],
        *,
        fraction: float = 1.0,
        skip_existing: bool = False,
    ) -> None:
        judge_names = ", ".join([f"'{judge.name}'" for judge in judges])
        message = f"Started automated judging task for {judge_names}"
        models = ModelService.get_all(project_slug)
        api_task = TaskService.create(project_slug, api.TaskType.AUTO_JUDGE, message)
        task = TaskService.Task(project_slug, api_task)
        with ThreadedExecutor(8) as executor:
            TaskService._auto_judge_inner(
                project_slug, task, models, judges, executor, fraction=fraction, skip_existing=skip_existing
            )

    @staticmethod
    def auto_judge_by_models(
        project_slug: str,
        models: list[api.Model],
        *,
        fraction: float = 1.0,
        skip_existing: bool = False,
    ) -> None:
        model_names = ", ".join([f"'{m.name}'" for m in models])
        all_judges = JudgeService.get_all(project_slug)
        enabled_judges = [j for j in all_judges if j.enabled and j.judge_type is not JudgeType.HUMAN]
        if len(enabled_judges) == 0:
            logger.warning(f"No automated judges found, can't run automated judgement for {model_names}")
            return  # do nothing if no judges are configured, do not create a task
        message = f"Started automated judging task for {model_names}"
        api_task = TaskService.create(project_slug, api.TaskType.AUTO_JUDGE, message)
        task = TaskService.Task(project_slug, api_task)
        logger.info(message)
        with ThreadedExecutor(8) as executor:
            TaskService._auto_judge_inner(
                project_slug, task, models, enabled_judges, executor, fraction=fraction, skip_existing=skip_existing
            )

    @staticmethod
    def _auto_judge_inner(
        project_slug: str,
        task: "TaskService.Task",
        models: list[api.Model],
        judges: list[api.Judge],
        executor: JudgeExecutor,
        *,
        fraction: float = 1.0,
        skip_existing: bool = False,
    ) -> None:
        t_start = time.time()
        try:
            # 1. instantiate judge(s)
            task.update(f"Using {len(judges)} judge(s):")
            for j in judges:
                task.update(f"  * {j.name}")
            wrappers = [retrying_wrapper, fixing_wrapper, ab_shuffling_wrapper]
            automated_judges = [judge_factory(j, wrappers=wrappers) for j in judges]

            # 2. get pairs eligible for judging
            df_h2hs = [HeadToHeadService.get_df(project_slug, api.HeadToHeadsRequest(model_a_id=m.id)) for m in models]
            df_h2h = pd.concat(df_h2hs)
            if len(df_h2h) == 0:
                message = "No head-to-heads found, exiting"
                logger.warning(message)
                task.update(message, status=api.TaskStatus.COMPLETED, progress=1)
                return
            df_h2h["response_id_slug"] = df_h2h.apply(lambda r: id_slug(r.response_a_id, r.response_b_id), axis=1)
            df_h2h = df_h2h.drop_duplicates(subset=["response_id_slug"], keep="first")

            n_models = len(set(df_h2h.model_a_id) | set(df_h2h.model_b_id))
            task.update(f"Found {len(df_h2h)} total head-to-heads between {n_models} model(s) to judge")

            if fraction < 1:
                n_total = len(df_h2h)
                df_h2h = df_h2h.sample(frac=fraction)
                task.update(f"Using subset of {len(df_h2h)} out of {n_total} head-to-heads ({int(100 * fraction)}%)")

            # 3. stream judgement requests
            judges_with_h2hs: list[tuple[AutomatedJudge, list[api.HeadToHead]]] = []
            for judge in automated_judges:
                head_to_heads = [
                    api.HeadToHead(r.prompt, r.response_a_id, r.response_a, r.response_b_id, r.response_b)
                    for r in df_h2h.itertuples()
                    if not skip_existing or judge.name not in {h["judge_name"] for h in r.history}
                ]
                if skip_existing:
                    n_skipping = len(df_h2h) - len(head_to_heads)
                    message = (
                        f"Skipping {n_skipping} for '{judge.name}' with existing votes, {len(head_to_heads)} to run"
                    )
                    logger.info(message)
                    task.update(message)
                if len(head_to_heads) == 0:
                    logger.warning(f"No head-to-heads without votes found for '{judge.name}', skipping this judge")
                else:
                    judges_with_h2hs.append((judge, head_to_heads))

            if len(judges_with_h2hs) == 0:
                message = "No head-to-heads without votes found for any judges, exiting"
                logger.warning(message)
                task.update(message, status=api.TaskStatus.COMPLETED, progress=1)
                return

            responses: dict[str, list[tuple[int, int, str]]] = defaultdict(lambda: [])
            n_h2h_by_judge_name = {judge.name: len(h2hs) for judge, h2hs in judges_with_h2hs}
            n_total = sum(len(h2hs) for _, h2hs in judges_with_h2hs)
            t_start_judging = time.time()
            for judge, h2h, winner in executor.execute(judges_with_h2hs):
                responses[judge.name].append((h2h.response_a_id, h2h.response_b_id, winner))
                n_this_judge = len(responses[judge.name])
                n_responses = sum(len(r) for r in responses.values())
                progress = 0.95 * (n_responses / n_total)
                if n_this_judge % 10 == 0:
                    message = f"Judged {n_this_judge} of {n_h2h_by_judge_name[judge.name]} with '{judge.name}'"
                    task.update(message, progress=progress)
                if n_this_judge == n_h2h_by_judge_name[judge.name]:
                    message = (
                        f"Judge '{judge.name}' finished judging {n_h2h_by_judge_name[judge.name]} head-to-heads in "
                        f"{time.time() - t_start_judging:0.1f} seconds"
                    )
                    task.update(message, progress=progress)
                    judge.log_usage()

            # TODO: stream to database?
            # 4. upload judgements to database
            judge_id_by_name = {j.name: j.id for j in judges}
            dfs_h2h_judged = []
            for judge_name, judge_responses in responses.items():
                df_h2h_judged = df_h2h.copy()
                df_h2h_judged["judge_id"] = judge_id_by_name[judge_name]
                df_judgement = pd.DataFrame(judge_responses, columns=["response_a_id", "response_b_id", "winner"])
                df_h2h_judged = pd.merge(df_h2h_judged, df_judgement, on=["response_a_id", "response_b_id"], how="left")
                df_h2h_judged = df_h2h_judged.dropna(subset=["winner"])
                dfs_h2h_judged.append(df_h2h_judged)
            df_h2h_judged_all = pd.concat(dfs_h2h_judged)
            HeadToHeadService.upload_head_to_heads(project_slug, df_h2h_judged_all)

            # 6. recompute elo scores and confidence intervals
            task.update("Recomputing leaderboard rankings", progress=0.96)
            EloService.reseed_scores(project_slug)
            message = f"Completed automated judging in {time.time() - t_start:0.1f} seconds"
            task.update(message, progress=1, status=api.TaskStatus.COMPLETED)
            logger.info(message)
        except Exception as e:
            task.update(f"Failed ({e})", status=api.TaskStatus.FAILED)
            message = "See AutoArena service logs for more information"
            task.update(message, status=api.TaskStatus.FAILED)
            logger.error(f"Automated judgement failed: {e}")
            raise e

    class Task:
        def __init__(self, project_slug: str, task: api.Task):
            self._project_slug = project_slug
            self._task = task

        def update(
            self,
            log: str,
            progress: Optional[float] = None,
            status: api.TaskStatus = api.TaskStatus.IN_PROGRESS,
        ) -> None:
            with ProjectService.connect(self._project_slug) as conn:
                log = f"{TaskService._time_slug()} {log}"
                conn.execute(
                    """
                    UPDATE task
                    SET progress = IFNULL($progress, progress),
                        status = $status,
                        logs = logs || '\n' || $log
                    WHERE id = $id
                    """,
                    dict(id=self._task.id, log=log, progress=progress, status=status.value),
                )
