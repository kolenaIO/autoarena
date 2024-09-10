import time
from collections import defaultdict
from datetime import datetime
from typing import Optional

import pandas as pd
from loguru import logger

from autoarena.api import api
from autoarena.api.api import JudgeType
from autoarena.judge.base import Judge
from autoarena.judge.executor import ThreadedExecutor
from autoarena.judge.factory import judge_factory
from autoarena.judge.utils import ABShufflingJudge, FixingJudge, RetryingJudge
from autoarena.service.elo import EloService
from autoarena.service.head_to_head import HeadToHeadService
from autoarena.service.judge import JudgeService
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
    def update(
        project_slug: str,
        task_id: int,
        log: str,
        progress: Optional[float] = None,
        status: api.TaskStatus = api.TaskStatus.IN_PROGRESS,
    ) -> None:
        with ProjectService.connect(project_slug) as conn:
            conn.execute(
                """
                UPDATE task
                SET progress = IFNULL($progress, progress),
                    status = $status,
                    logs = logs || '\n' || $log
                WHERE id = $id
                """,
                dict(id=task_id, log=f"{TaskService._time_slug()} {log}", progress=progress, status=status.value),
            )

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
        task_id = TaskService.create(project_slug, api.TaskType.RECOMPUTE_LEADERBOARD).id
        try:
            EloService.reseed_scores(project_slug)
        finally:
            TaskService.update(project_slug, task_id, "Done", progress=1, status=api.TaskStatus.COMPLETED)

    @staticmethod
    def auto_judge(project_slug: str, models: list[api.Model]) -> None:
        model_names = ", ".join([f"'{m.name}'" for m in models])
        # 1. get judge(s) configured for judging
        all_judges = JudgeService.get_all(project_slug)
        enabled_auto_judges = [j for j in all_judges if j.enabled and j.judge_type is not JudgeType.HUMAN]
        if len(enabled_auto_judges) == 0:
            logger.warning(f"No automated judges found, can't run automated judgement for {model_names}")
            return  # do nothing if no judges are configured, do not create a task
        t_start = time.time()
        message = f"Started automated judging task for {model_names}"
        task_id = TaskService.create(project_slug, api.TaskType.AUTO_JUDGE, message).id
        logger.info(message)

        try:
            # 2. instantiate judge(s)
            TaskService.update(project_slug, task_id, f"Using {len(enabled_auto_judges)} judge(s):")
            for j in enabled_auto_judges:
                TaskService.update(project_slug, task_id, f"  * {j.name}")
            wrappers = [RetryingJudge, FixingJudge, ABShufflingJudge]
            judges: list[Judge] = [judge_factory(j, wrappers=wrappers) for j in enabled_auto_judges]

            # 3. get pairs eligible for judging
            df_h2hs = [HeadToHeadService.get_df(project_slug, api.HeadToHeadsRequest(model_a_id=m.id)) for m in models]
            df_h2h = pd.concat(df_h2hs)
            if len(df_h2h) == 0:
                message = "No head-to-heads found, exiting"
                logger.warning(message)
                TaskService.update(project_slug, task_id, message, status=api.TaskStatus.COMPLETED, progress=1)
                return
            df_h2h["response_id_slug"] = df_h2h.apply(lambda r: id_slug(r.response_a_id, r.response_b_id), axis=1)
            df_h2h = df_h2h.drop_duplicates(subset=["response_id_slug"], keep="first")
            message = f"Found {len(df_h2h)} head-to-heads versus {len(set(df_h2h.model_b_id))} model(s) to judge"
            TaskService.update(project_slug, task_id, message)

            # 4. stream judgement requests
            head_to_heads = [
                api.HeadToHead(**r)
                for _, r in df_h2h[["prompt", "response_a_id", "response_a", "response_b_id", "response_b"]].iterrows()
            ]
            executor = ThreadedExecutor(4)
            responses: dict[str, list[tuple[int, int, str]]] = defaultdict(lambda: [])
            n_h2h = len(head_to_heads)
            n_total = n_h2h * len(judges)
            t_start_judging = time.time()
            for judge, h2h, winner in executor.execute(judges, head_to_heads):
                responses[judge.name].append((h2h.response_a_id, h2h.response_b_id, winner))
                n_this_judge = len(responses[judge.name])
                n_responses = sum(len(r) for r in responses.values())
                progress = 0.95 * (n_responses / n_total)
                if n_this_judge % 10 == 0:
                    message = f"Judged {n_this_judge} of {n_h2h} with '{judge.name}'"
                    TaskService.update(project_slug, task_id, message, progress=progress)
                if n_this_judge == len(head_to_heads):
                    message = (
                        f"Judge '{judge.name}' finished judging {n_h2h} head-to-heads in "
                        f"{time.time() - t_start_judging:0.1f} seconds"
                    )
                    TaskService.update(project_slug, task_id, message, progress=progress)

            # TODO: stream to database?
            # 5. upload judgements to database
            judge_id_by_name = {j.name: j.id for j in enabled_auto_judges}
            dfs_h2h_judged = []
            for judge_name, judge_responses in responses.items():
                df_h2h_judged = df_h2h.copy()
                df_h2h_judged["judge_id"] = judge_id_by_name[judge_name]
                df_judgement = pd.DataFrame(judge_responses, columns=["response_a_id", "response_b_id", "winner"])
                df_h2h_judged = pd.merge(df_h2h_judged, df_judgement, on=["response_a_id", "response_b_id"], how="left")
                dfs_h2h_judged.append(df_h2h_judged)
            # randomize order of ratings to avoid biased elos when multiple judges are present
            df_h2h_judged_all = pd.concat(dfs_h2h_judged).sample(frac=1.0)  # noqa: F841
            HeadToHeadService.upload_head_to_heads(project_slug, df_h2h_judged_all)

            # 6. recompute elo scores and confidence intervals
            TaskService.update(project_slug, task_id, "Recomputing leaderboard rankings", progress=0.96)
            EloService.reseed_scores(project_slug)
            message = f"Completed automated judging in {time.time() - t_start:0.1f} seconds"
            TaskService.update(project_slug, task_id, message, progress=1, status=api.TaskStatus.COMPLETED)
            logger.info(message)
        except Exception as e:
            TaskService.update(project_slug, task_id, f"Failed ({e})", status=api.TaskStatus.FAILED)
            message = "See AutoArena service logs for more information"
            TaskService.update(project_slug, task_id, message, status=api.TaskStatus.FAILED)
            logger.error(f"Automated judgement failed: {e}")
            raise e
