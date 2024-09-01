from datetime import datetime

from autostack.api import api
from autostack.store.database import get_database_connection


class TaskService:
    @staticmethod
    def get_all(project_id: int) -> list[api.Task]:
        with get_database_connection() as conn:
            df_task = conn.execute(
                "SELECT id, task_type, created, progress, status FROM task WHERE project_id = $project_id",
                dict(project_id=project_id),
            ).df()
        return [api.Task(**r) for _, r in df_task.iterrows()]

    @staticmethod
    def create(project_id: int, task_type: api.TaskType, status: str = "Started") -> api.Task:
        with get_database_connection() as conn:
            ((task_id, created, progress, status),) = conn.execute(
                """
                INSERT INTO task (project_id, task_type, status)
                VALUES ($project_id, $task_type, $status)
                RETURNING id, created, progress, status
                """,
                dict(project_id=project_id, task_type=task_type, status=f"{TaskService._time_slug()} {status}"),
            ).fetchall()
        return api.Task(id=task_id, task_type=task_type, created=created, progress=progress, status=status)

    @staticmethod
    def update(task_id: int, status: str, progress: float) -> None:
        with get_database_connection() as conn:
            conn.execute(
                "UPDATE task SET progress = $progress, status = status || '\n' || $status WHERE id = $id",
                dict(id=task_id, status=f"{TaskService._time_slug()} {status}", progress=progress),
            )

    @staticmethod
    def finish(task_id: int, status: str = "Done") -> None:
        TaskService.update(task_id, status, progress=1)

    @staticmethod
    def _time_slug() -> str:
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
