from loguru import logger

from autoarena.api import api
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
                    SUM(IF(h.id IS NOT NULL, 1, 0)) AS n_votes
                FROM judge j
                LEFT JOIN head_to_head h ON h.judge_id = j.id
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
            n_votes=0,
        )

    # TODO: is this necessary?
    @staticmethod
    def create_human_judge(project_slug: str) -> api.Judge:
        with ProjectService.connect(project_slug) as conn:
            conn.execute(
                """
                INSERT INTO judge (judge_type, name, description, enabled)
                VALUES ($judge_type, $name, $description, TRUE)
                ON CONFLICT (name) DO NOTHING
            """,
                dict(
                    judge_type=api.JudgeType.HUMAN.value,
                    name=api.JudgeType.HUMAN.value,
                    description="Manual ratings submitted via the 'Head-to-Head' tab",
                ),
            )
        # TODO: this is a little lazy but ¯\_(ツ)_/¯
        return [j for j in JudgeService.get_all(project_slug) if j.judge_type is api.JudgeType.HUMAN][0]

    @staticmethod
    def update(project_slug: str, judge_id: int, request: api.UpdateJudgeRequest) -> api.Judge:
        with ProjectService.connect(project_slug) as conn:
            conn.execute(
                "UPDATE judge SET enabled = $enabled WHERE id = $judge_id",
                dict(judge_id=judge_id, enabled=request.enabled),
            )
        return [j for j in JudgeService.get_all(project_slug) if j.id == judge_id][0]

    @staticmethod
    def delete(project_slug: str, judge_id: int) -> None:
        with ProjectService.connect(project_slug) as conn:
            conn.execute("DELETE FROM head_to_head WHERE judge_id = $judge_id", dict(judge_id=judge_id))
            conn.execute("DELETE FROM judge WHERE id = $judge_id", dict(judge_id=judge_id))

    @staticmethod
    def check_can_access(judge_type: api.JudgeType) -> bool:
        try:
            verify_judge_type_environment(judge_type)
            return True
        except Exception as e:
            logger.warning(f"Missing environment configuration necessary to run '{judge_type}' judge: {e}")
            return False
