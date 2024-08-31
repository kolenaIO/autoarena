from datetime import datetime

import numpy as np

from autostack.api import api
from autostack.judge.base import Judge
from autostack.store.database import get_database_connection


class ProjectService:
    @staticmethod
    def get_all() -> list[api.Project]:
        with get_database_connection() as conn:
            df_project = conn.execute("SELECT id, name, created FROM project").df()
        return [api.Project(**r) for _, r in df_project.iterrows()]

    @staticmethod
    def create_idempotent(request: api.CreateProjectRequest) -> api.Project:
        with get_database_connection() as conn:
            params = dict(name=request.name)
            conn.execute("INSERT INTO project (name) VALUES ($name) ON CONFLICT (name) DO NOTHING", params)
            ((project_id, name, created),) = conn.execute(
                "SELECT id, name, created FROM project WHERE name = $name",
                params,
            ).fetchall()
        return api.Project(id=project_id, name=name, created=created)


class JudgeService:
    @staticmethod
    def get_all(project_id: int) -> list[api.Judge]:
        with get_database_connection() as conn:
            df_task = conn.execute(
                "SELECT id, judge_type, created, name, description, enabled FROM judge WHERE project_id = $project_id",
                dict(project_id=project_id),
            ).df()
        # TODO: this throws a pydantic warning due to enum serialization shenanigans
        return [api.Judge(**r) for _, r in df_task.iterrows()]

    @staticmethod
    def create(request: api.CreateJudgeRequest) -> api.Judge:
        with get_database_connection() as conn:
            ((judge_id, created, enabled),) = conn.execute(
                """
                INSERT INTO judge (judge_type, project_id, name, description, enabled)
                VALUES ($judge_type, $project_id, $name, $description, TRUE)
                RETURNING id, created, enabled
            """,
                dict(
                    project_id=request.project_id,
                    judge_type=request.judge_type.value,
                    name=request.name,
                    description=request.description,
                ),
            ).fetchall()
        return api.Judge(
            id=judge_id,
            judge_type=request.judge_type,
            created=created,
            name=request.name,
            description=request.description,
            enabled=enabled,
        )

    @staticmethod
    def create_idempotent(project_id: int, judge: Judge) -> api.Judge:
        with get_database_connection() as conn:
            conn.execute(
                """
                INSERT INTO judge (judge_type, project_id, name, description, enabled)
                VALUES ($judge_type, $project_id, $name, $description, TRUE)
                ON CONFLICT (project_id, name) DO NOTHING
            """,
                dict(
                    project_id=project_id,
                    judge_type=judge.judge_type.value,
                    name=judge.name,
                    description=judge.description,
                ),
            )
        # TODO: this is a little lazy but ¯\_(ツ)_/¯
        return [j for j in JudgeService.get_all(project_id) if j.name == judge.name][0]

    @staticmethod
    def update(request: api.UpdateJudgeRequest) -> api.Judge:
        with get_database_connection() as conn:
            conn.execute(
                "UPDATE judge SET enabled = $enabled WHERE id = $judge_id",
                dict(judge_id=request.judge_id, enabled=request.enabled),
            )
        return [j for j in JudgeService.get_all(request.project_id) if j.name == request.judge_id][0]

    @staticmethod
    def delete(judge_id: int) -> None:
        with get_database_connection() as conn:
            # TODO: duckdb doesn't support cascading deletes so this fails if this judge has submitted ratings
            conn.execute("DELETE FROM judge WHERE id = $judge_id", dict(judge_id=judge_id))


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


class ModelService:
    @staticmethod
    def get_all(project_id: int) -> list[api.Model]:
        with get_database_connection() as conn:
            df_model = conn.execute(
                """
                WITH datapoint_count AS (
                    SELECT m.id AS model_id, COUNT(1) AS datapoint_count
                    FROM model m
                    JOIN result r ON m.id = r.model_id
                    GROUP BY m.id
                ), vote_count_a AS (
                    SELECT m.id AS model_id, COUNT(1) AS vote_count
                    FROM model m
                    JOIN result r ON r.model_id = m.id
                    JOIN battle b ON r.id = b.result_a_id
                    GROUP BY m.id
                ), vote_count_b AS (
                    SELECT m.id AS model_id, COUNT(1) AS vote_count
                    FROM model m
                    JOIN result r ON r.model_id = m.id
                    JOIN battle b ON r.id = b.result_b_id
                    GROUP BY m.id
                )
                SELECT
                    id,
                    name,
                    created,
                    elo,
                    q025,
                    q975,
                    IFNULL(dc.datapoint_count, 0) AS datapoints,
                    IFNULL(vca.vote_count, 0) + IFNULL(vcb.vote_count, 0) AS votes
                FROM model m
                LEFT JOIN datapoint_count dc ON m.id = dc.model_id
                LEFT JOIN vote_count_a vca ON m.id = vca.model_id
                LEFT JOIN vote_count_b vcb ON m.id = vcb.model_id
                WHERE project_id = ?
            """,
                [project_id],
            ).df()
        df_model = df_model.replace({np.nan: None})
        return [api.Model(**r) for _, r in df_model.iterrows()]
