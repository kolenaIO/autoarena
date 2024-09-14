import dataclasses
import time
from collections import defaultdict
from datetime import datetime
from typing import Optional

import pandas as pd
from loguru import logger
from pydantic.dataclasses import dataclass

from autoarena.api import api
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.executor import ThreadedExecutor, JudgeExecutor
from autoarena.judge.factory import judge_factory
from autoarena.judge.wrapper import ab_shuffling_wrapper, fixing_wrapper, retrying_wrapper, JudgeWrapper
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
    def update(
        project_slug: str,
        task_id: int,
        log: str,
        progress: Optional[float] = None,
        status: api.TaskStatus = api.TaskStatus.IN_PROGRESS,
    ) -> None:
        with ProjectService.connect(project_slug) as conn:
            log = f"{TaskService._time_slug()} {log}"
            conn.execute(
                """
                UPDATE task
                SET progress = IFNULL($progress, progress),
                    status = $status,
                    logs = logs || '\n' || $log
                WHERE id = $id
                """,
                dict(id=task_id, log=log, progress=progress, status=status.value),
            )

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
    def auto_judge(
        project_slug: str,
        *,
        models: Optional[list[api.Model]] = None,
        judges: Optional[list[api.Judge]] = None,
        fraction: float = 1.0,
        skip_existing: bool = False,
    ) -> None:
        auto_judge_task = AutoJudgeTask.create(project_slug, models, judges, fraction, skip_existing)
        if auto_judge_task is None:
            return
        try:
            with ThreadedExecutor(8) as executor:
                auto_judge_task.run(executor)
        except Exception as e:
            TaskService.update(project_slug, auto_judge_task.task_id, f"Failed ({e})", status=api.TaskStatus.FAILED)
            message = "See AutoArena service logs for more information"
            TaskService.update(project_slug, auto_judge_task.task_id, message, status=api.TaskStatus.FAILED)
            logger.error(f"Automated judgement failed: {e}")
            raise e


@dataclass(frozen=True)
class AutoJudgeTask:
    project_slug: str
    task_id: int
    models: list[api.Model]
    judges: list[api.Judge]
    fraction: float = 1.0
    skip_existing: bool = False
    t_start: float = dataclasses.field(default_factory=time.time)
    judge_wrappers: list[JudgeWrapper] = dataclasses.field(
        default_factory=lambda: [retrying_wrapper, fixing_wrapper, ab_shuffling_wrapper]
    )

    def __post_init__(self) -> None:
        if self.fraction <= 0 or self.fraction > 1:
            raise ValueError(f"Invalid fraction: {self.fraction} must be on (0,1]")
        if len(self.models) == 0:
            raise ValueError("No models provided")
        if len(self.judges) == 0:
            raise ValueError("No judges provided")

    @classmethod
    def create(
        cls,
        project_slug: str,
        models: Optional[list[api.Model]] = None,
        judges: Optional[list[api.Judge]] = None,
        fraction: float = 1.0,
        skip_existing: bool = False,
    ) -> Optional["AutoJudgeTask"]:
        models = models or ModelService.get_all(project_slug)
        judges = judges or JudgeService.get_all(project_slug)
        enabled_judges = [j for j in judges if j.enabled and j.judge_type is not api.JudgeType.HUMAN]
        if len(enabled_judges) == 0:
            logger.warning("No enabled judges found, can't run automated judgement")
            return None  # do nothing if no judges are configured, do not create a task
        message = f"Started automated judging task using {len(enabled_judges)} judge(s)"
        task_id = TaskService.create(project_slug, api.TaskType.AUTO_JUDGE, message).id
        logger.info(message)
        return AutoJudgeTask(project_slug, task_id, models, enabled_judges, fraction, skip_existing)

    def log(
        self,
        message: str,
        status: api.TaskStatus = api.TaskStatus.IN_PROGRESS,
        progress: Optional[float] = None,
        level: str = "INFO",
    ) -> None:
        TaskService.update(self.project_slug, self.task_id, message, status=status, progress=progress)
        logger.log(level, message)

    # this is a beast, but most of the bulk comes from logging
    def run(self, executor: JudgeExecutor) -> None:
        h2h_requests = [api.HeadToHeadsRequest(model_a_id=m.id) for m in self.models]
        df_h2h = pd.concat([HeadToHeadService.get_df(self.project_slug, request) for request in h2h_requests])
        if len(df_h2h) == 0:
            self.log("No head-to-heads found, exiting", status=api.TaskStatus.COMPLETED, progress=1, level="WARNING")
            return

        df_h2h["response_id_slug"] = df_h2h.apply(lambda r: id_slug(r.response_a_id, r.response_b_id), axis=1)
        df_h2h = df_h2h.drop_duplicates(subset=["response_id_slug"], keep="first")
        n_models = len(set(df_h2h.model_a_id) | set(df_h2h.model_b_id))
        self.log(f"Found {len(df_h2h)} total head-to-heads between {n_models} model(s) to judge")

        if self.fraction < 1:
            n_total = len(df_h2h)
            df_h2h = df_h2h.sample(frac=self.fraction)
            self.log(f"Using subset of {len(df_h2h)} out of {n_total} head-to-heads ({int(100 * self.fraction)}%)")

        # 2. instantiate judge(s)
        self.log(f"Running {len(self.judges)} judge(s):")
        for j in self.judges:
            self.log(f"  * {j.name}")

        # 3. assemble head-to-heads for judging
        judges_with_h2hs: list[tuple[AutomatedJudge, list[api.HeadToHead]]] = []
        for judge in self.judges:
            automated_judge = judge_factory(judge, wrappers=self.judge_wrappers)
            head_to_heads = [
                api.HeadToHead(r.prompt, r.response_a_id, r.response_a, r.response_b_id, r.response_b)
                for r in df_h2h.itertuples()
                if not self.skip_existing or judge.name not in {h["judge_name"] for h in r.history}
            ]
            n_skipping = len(df_h2h) - len(head_to_heads)
            if n_skipping > 0:
                self.log(f"Skipping {n_skipping} for '{judge.name}' with existing votes, {len(head_to_heads)} to run")
            if len(head_to_heads) == 0:
                message = f"No head-to-heads without votes found for '{judge.name}', skipping this judge"
                self.log(message, level="WARNING")
            else:
                judges_with_h2hs.append((automated_judge, head_to_heads))

        if len(judges_with_h2hs) == 0:
            message = "No head-to-heads without votes found for any judges, exiting"
            self.log(message, status=api.TaskStatus.COMPLETED, progress=1, level="WARNING")
            return

        responses: dict[str, list[tuple[int, int, str]]] = defaultdict(lambda: [])
        n_h2h_by_judge_name = {judge.name: len(h2hs) for judge, h2hs in judges_with_h2hs}
        n_total = sum(len(h2hs) for _, h2hs in judges_with_h2hs)
        t_start_judging = time.time()
        for auto_judge, h2h, winner in executor.execute(judges_with_h2hs):
            responses[auto_judge.name].append((h2h.response_a_id, h2h.response_b_id, winner))
            n_this_judge = len(responses[auto_judge.name])
            n_responses = sum(len(r) for r in responses.values())
            progress = 0.95 * (n_responses / n_total)
            if n_this_judge % 10 == 0:
                message = f"Judged {n_this_judge} of {n_h2h_by_judge_name[auto_judge.name]} with '{auto_judge.name}'"
                self.log(message, progress=progress)
            if n_this_judge == n_h2h_by_judge_name[auto_judge.name]:
                message = (
                    f"Judge '{auto_judge.name}' finished judging {n_h2h_by_judge_name[auto_judge.name]} head-to-heads "
                    f"in {time.time() - t_start_judging:0.1f} seconds"
                )
                self.log(message, progress=progress)
                auto_judge.log_usage()

        # TODO: stream to database?
        # 4. upload judgements to database
        judge_id_by_name = {j.name: j.id for j in self.judges}
        dfs_h2h_judged = []
        for judge_name, judge_responses in responses.items():
            df_h2h_judged = df_h2h.copy()
            df_h2h_judged["judge_id"] = judge_id_by_name[judge_name]
            df_judgement = pd.DataFrame(judge_responses, columns=["response_a_id", "response_b_id", "winner"])
            df_h2h_judged = pd.merge(df_h2h_judged, df_judgement, on=["response_a_id", "response_b_id"], how="left")
            df_h2h_judged = df_h2h_judged.dropna(subset=["winner"])
            dfs_h2h_judged.append(df_h2h_judged)
        df_h2h_judged_all = pd.concat(dfs_h2h_judged)
        HeadToHeadService.upload_head_to_heads(self.project_slug, df_h2h_judged_all)

        # 6. recompute elo scores and confidence intervals
        self.log("Recomputing leaderboard rankings", progress=0.975)
        EloService.reseed_scores(self.project_slug)
        message = f"Completed automated judging in {time.time() - self.t_start:0.1f} seconds"
        self.log(message, progress=1, status=api.TaskStatus.COMPLETED, level="SUCCESS")
