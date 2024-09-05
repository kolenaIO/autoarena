from autoarena.api import api
from autoarena.judge.base import Judge
from autoarena.judge.utils import BASIC_SYSTEM_PROMPT
from autoarena.store.database import get_database_connection


class JudgeService:
    @staticmethod
    def get_default_system_prompt() -> str:
        return BASIC_SYSTEM_PROMPT

    @staticmethod
    def get_project_id(judge_id: int) -> int:
        with get_database_connection() as conn:
            params = dict(judge_id=judge_id)
            ((project_id,),) = conn.execute("SELECT project_id FROM judge WHERE id = $judge_id", params).fetchall()
        return project_id

    @staticmethod
    def get_all(project_id: int) -> list[api.Judge]:
        with get_database_connection() as conn:
            df_task = conn.execute(
                """
                SELECT
                    j.id,
                    j.judge_type,
                    j.created,
                    j.name,
                    j.model_name,
                    j.system_prompt,
                    j,description,
                    j.enabled,
                    SUM(IF(b.id IS NOT NULL, 1, 0)) AS votes
                FROM judge j
                LEFT JOIN battle b ON b.judge_id = j.id
                WHERE j.project_id = $project_id
                GROUP BY
                    j.id,
                    j.project_id,
                    j.judge_type,
                    j.created,
                    j.name,
                    j.model_name,
                    j.system_prompt,
                    j.description,
                    j.enabled
                ORDER BY j.id
                """,
                dict(project_id=project_id),
            ).df()
        return [api.Judge(**r) for _, r in df_task.iterrows()]

    @staticmethod
    def create(request: api.CreateJudgeRequest) -> api.Judge:
        with get_database_connection() as conn:
            ((judge_id, created, enabled),) = conn.execute(
                """
                INSERT INTO judge (judge_type, project_id, name, model_name, system_prompt, description, enabled)
                VALUES ($judge_type, $project_id, $name, $model_name, $system_prompt, $description, TRUE)
                RETURNING id, created, enabled
            """,
                dict(
                    project_id=request.project_id,
                    judge_type=request.judge_type.value,
                    name=request.name,
                    model_name=request.model_name,
                    system_prompt=request.system_prompt,
                    description=request.description,
                ),
            ).fetchall()
        return api.Judge(
            id=judge_id,
            judge_type=request.judge_type,
            created=created,
            name=request.name,
            model_name=request.model_name,
            system_prompt=request.system_prompt,
            description=request.description,
            enabled=enabled,
            votes=0,
        )

    @staticmethod
    def create_idempotent(project_id: int, judge: Judge) -> api.Judge:
        with get_database_connection() as conn:
            conn.execute(
                """
                INSERT INTO judge (judge_type, project_id, name, model_name, system_prompt, description, enabled)
                VALUES ($judge_type, $project_id, $name, $model_name, $system_prompt, $description, TRUE)
                ON CONFLICT (project_id, name) DO NOTHING
            """,
                dict(
                    project_id=project_id,
                    judge_type=judge.judge_type.value,
                    name=judge.name,
                    model_name=judge.model_name,
                    system_prompt=judge.system_prompt,
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
        return [j for j in JudgeService.get_all(request.project_id) if j.id == request.judge_id][0]

    @staticmethod
    def delete(judge_id: int) -> None:
        with get_database_connection() as conn:
            conn.execute("DELETE FROM battle WHERE judge_id = $judge_id", dict(judge_id=judge_id))
            conn.execute("DELETE FROM judge WHERE id = $judge_id", dict(judge_id=judge_id))
