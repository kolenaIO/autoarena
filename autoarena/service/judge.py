from loguru import logger
import pandas as pd

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
            df = pd.read_sql_query(
                """
                SELECT
                    j.id,
                    j.judge_type,
                    strftime('%Y-%m-%dT%H:%M:%SZ', j.created) AS created,
                    j.name,
                    j.model_name,
                    j.system_prompt,
                    j.description,
                    j.enabled,
                    SUM(IIF(h.id IS NOT NULL, 1, 0)) AS n_votes
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
                conn,
            )
        judge_types = {j for j in api.JudgeType}
        df["judge_type"] = df["judge_type"].apply(lambda j: j if j in judge_types else api.JudgeType.UNRECOGNIZED.value)
        return [api.Judge(**r) for _, r in df.iterrows()]

    @staticmethod
    def get_df_vote(project_slug: str, judge_id: int) -> pd.DataFrame:
        with ProjectService.connect(project_slug) as conn:
            return pd.read_sql_query(
                """
                SELECT
                    j.name as judge,
                    ra.prompt as prompt,
                    ma.name as model_a,
                    mb.name as model_b,
                    ra.response as response_a,
                    rb.response as response_b,
                    h2h.winner as winner
                FROM judge j
                JOIN head_to_head h2h ON j.id = h2h.judge_id
                JOIN response ra ON ra.id = h2h.response_a_id
                JOIN response rb ON rb.id = h2h.response_b_id
                JOIN model ma ON ra.model_id = ma.id
                JOIN model mb ON rb.model_id = mb.id
                WHERE j.id = :judge_id
                ORDER BY h2h.id
                """,
                conn,
                params=dict(judge_id=judge_id),
            )

    @staticmethod
    def create(project_slug: str, request: api.CreateJudgeRequest) -> api.Judge:
        with ProjectService.connect(project_slug, commit=True) as conn:
            cur = conn.cursor()
            ((judge_id, created, enabled),) = cur.execute(
                """
                INSERT INTO judge (judge_type, name, model_name, system_prompt, description, enabled)
                VALUES (:judge_type, :name, :model_name, :system_prompt, :description, TRUE)
                RETURNING id, strftime('%Y-%m-%dT%H:%M:%SZ', created), enabled
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

    @staticmethod
    def create_human_judge(project_slug: str, name: str) -> None:
        with ProjectService.connect(project_slug, commit=True) as conn:
            conn.cursor().execute(
                """
                INSERT INTO judge (judge_type, name, description, enabled)
                VALUES (:judge_type, :name, :description, TRUE)
                ON CONFLICT (name) DO NOTHING
            """,
                dict(
                    judge_type=api.JudgeType.HUMAN.value,
                    name=name,
                    description="Manual votes submitted via the 'Head-to-Head' tab",
                ),
            )

    @staticmethod
    def update(project_slug: str, judge_id: int, request: api.UpdateJudgeRequest) -> api.Judge:
        with ProjectService.connect(project_slug, commit=True) as conn:
            conn.cursor().execute(
                "UPDATE judge SET enabled = :enabled WHERE id = :judge_id",
                dict(judge_id=judge_id, enabled=request.enabled),
            )
        return [j for j in JudgeService.get_all(project_slug) if j.id == judge_id][0]

    @staticmethod
    def delete(project_slug: str, judge_id: int) -> None:
        with ProjectService.connect(project_slug, commit=True) as conn:
            conn.execute("DELETE FROM judge WHERE id = :judge_id", dict(judge_id=judge_id))

    @staticmethod
    def check_can_access(judge_type: api.JudgeType) -> bool:
        try:
            verify_judge_type_environment(judge_type)
            return True
        except Exception as e:
            logger.warning(f"Missing environment configuration necessary to run '{judge_type}' judge: {e}")
            return False
