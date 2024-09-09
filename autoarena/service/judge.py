from loguru import logger

from autoarena.api import api
from autoarena.judge.base import Judge
from autoarena.judge.factory import verify_judge_type_environment
from autoarena.judge.utils import BASIC_SYSTEM_PROMPT
from autoarena.service.project import ProjectService


class JudgeService:
    @staticmethod
    def get_default_system_prompt() -> str:
        return BASIC_SYSTEM_PROMPT

    @staticmethod
    def get_all(project_slug: str) -> list[api.Judge]:
        with ProjectService.connect(project_slug) as conn:
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
                GROUP BY
                    j.id,
                    j.judge_type,
                    j.created,
                    j.name,
                    j.model_name,
                    j.system_prompt,
                    j.description,
                    j.enabled
                ORDER BY j.id
                """,
            ).df()
        return [api.Judge(**r) for _, r in df_task.iterrows()]

    @staticmethod
    def create(project_slug: str, request: api.CreateJudgeRequest) -> api.Judge:
        with ProjectService.connect(project_slug) as conn:
            ((judge_id, created, enabled),) = conn.execute(
                """
                INSERT INTO judge (judge_type, name, model_name, system_prompt, description, enabled)
                VALUES ($judge_type, $name, $model_name, $system_prompt, $description, TRUE)
                RETURNING id, created, enabled
            """,
                dict(
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
    def create_idempotent(project_slug: str, judge: Judge) -> api.Judge:
        with ProjectService.connect(project_slug) as conn:
            conn.execute(
                """
                INSERT INTO judge (judge_type, name, model_name, system_prompt, description, enabled)
                VALUES ($judge_type, $name, $model_name, $system_prompt, $description, TRUE)
                ON CONFLICT (name) DO NOTHING
            """,
                dict(
                    judge_type=judge.judge_type.value,
                    name=judge.name,
                    model_name=judge.model_name,
                    system_prompt=judge.system_prompt,
                    description=judge.description,
                ),
            )
        # TODO: this is a little lazy but ¯\_(ツ)_/¯
        return [j for j in JudgeService.get_all(project_slug) if j.name == judge.name][0]

    @staticmethod
    def update(project_slug: str, request: api.UpdateJudgeRequest) -> api.Judge:
        with ProjectService.connect(project_slug) as conn:
            conn.execute(
                "UPDATE judge SET enabled = $enabled WHERE id = $judge_id",
                dict(judge_id=request.judge_id, enabled=request.enabled),
            )
        return [j for j in JudgeService.get_all(project_slug) if j.id == request.judge_id][0]

    @staticmethod
    def delete(project_slug: str, judge_id: int) -> None:
        with ProjectService.connect(project_slug) as conn:
            conn.execute("DELETE FROM battle WHERE judge_id = $judge_id", dict(judge_id=judge_id))
            conn.execute("DELETE FROM judge WHERE id = $judge_id", dict(judge_id=judge_id))

    @staticmethod
    def check_can_access(judge_type: api.JudgeType) -> bool:
        try:
            verify_judge_type_environment(judge_type)
            return True
        except Exception as e:
            logger.warning(f"Missing environment configuration necessary to run '{judge_type}' judge: {e}")
            return False
