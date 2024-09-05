from autoarena.api import api
from autoarena.judge.human import HumanJudge
from autoarena.service.judge import JudgeService
from autoarena.store.database import get_database_connection


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
        JudgeService.create_idempotent(project_id, HumanJudge())
        return api.Project(id=project_id, name=name, created=created)

    @staticmethod
    def delete(project_id: int) -> None:
        params = dict(project_id=project_id)
        with get_database_connection() as conn:  # wish duckdb had cascading deletes...
            conn.execute("DELETE FROM task WHERE project_id = $project_id", params)
            conn.execute(
                """
                DELETE FROM battle b
                WHERE EXISTS (
                    SELECT 1
                    FROM result r
                    JOIN model m ON m.id = r.model_id
                    WHERE (b.result_a_id = r.id OR b.result_b_id = r.id)
                    AND m.project_id = $project_id
                )
                """,
                params,
            )
            conn.execute(
                """
                DELETE FROM result r
                WHERE EXISTS (SELECT 1 FROM model m WHERE m.id = r.model_id AND m.project_id = $project_id)
                """,
                params,
            )
            conn.execute("DELETE FROM model WHERE project_id = $project_id", params)
            conn.execute("DELETE FROM judge WHERE project_id = $project_id", params)
            conn.execute("DELETE FROM project WHERE id = $project_id", params)
