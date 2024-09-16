import asyncio
import time
from datetime import datetime
from typing import Optional, AsyncIterator


from autoarena.api import api
from autoarena.error import NotFoundError
from autoarena.judge.executor import ThreadedExecutor
from autoarena.service.elo import EloService
from autoarena.service.project import ProjectService


class TaskService:
    @staticmethod
    def get_all(project_slug: str) -> list[api.Task]:
        with ProjectService.connect(project_slug) as conn:
            df_task = conn.execute("SELECT id, task_type, created, progress, status, logs FROM task").df()
        return [api.Task(**r) for _, r in df_task.iterrows()]

    @staticmethod
    def get(project_slug: str, task_id: int) -> api.Task:
        try:
            with ProjectService.connect(project_slug) as conn:
                df_task = conn.execute(
                    "SELECT id, task_type, created, progress, status, logs FROM task WHERE id = $task_id",
                    dict(task_id=task_id),
                ).df()
                return [api.Task(**r) for _, r in df_task.iterrows()][0]
        except IndexError:
            raise NotFoundError(f"Task with id '{task_id}' not found")

    @staticmethod
    async def get_stream(project_slug: str, task_id: int) -> AsyncIterator[api.Task]:
        prev: Optional[api.Task] = None
        while True:
            cur = TaskService.get(project_slug, task_id)
            if prev != cur:
                yield cur
            if cur.status in {api.TaskStatus.COMPLETED, api.TaskStatus.FAILED}:
                break
            prev = cur
            await asyncio.sleep(0.2)

    @staticmethod
    def has_active(project_slug: str) -> api.HasActiveTasks:
        with ProjectService.connect(project_slug) as conn:
            records = conn.execute(
                "SELECT 1 WHERE EXISTS (SELECT 1 FROM task WHERE status IN ($started, $in_progress))",
                dict(started=api.TaskStatus.STARTED.value, in_progress=api.TaskStatus.IN_PROGRESS.value),
            ).fetchall()
            return api.HasActiveTasks(has_active=len(records) > 0)

    @staticmethod
    async def has_active_stream(
        project_slug: str,
        timeout: Optional[float] = None,
    ) -> AsyncIterator[api.HasActiveTasks]:
        t0 = time.time()
        prev: Optional[api.HasActiveTasks] = None
        while timeout is None or time.time() - t0 < timeout:
            cur = TaskService.has_active(project_slug)
            if prev != cur:
                yield cur
            prev = cur
            await asyncio.sleep(1)

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
        from autoarena.task.auto_judge import AutoJudgeTask

        auto_judge_task = AutoJudgeTask.create(project_slug, models, judges, fraction, skip_existing)
        if auto_judge_task is not None:
            with ThreadedExecutor(8) as executor:
                auto_judge_task.run(executor)
