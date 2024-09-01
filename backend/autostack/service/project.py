from autostack.api import api
from autostack.judge.human import HumanJudge
from autostack.service.judge import JudgeService
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
        JudgeService.create_idempotent(project_id, HumanJudge())
        return api.Project(id=project_id, name=name, created=created)
