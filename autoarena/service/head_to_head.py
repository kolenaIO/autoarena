import dataclasses
import json

import pandas as pd
from loguru import logger

from autoarena.api import api
from autoarena.error import BadRequestError
from autoarena.service.elo import EloService
from autoarena.service.judge import JudgeService
from autoarena.service.project import ProjectService
from autoarena.store.database import temporary_table
from autoarena.store.utils import id_slug, check_required_columns


class HeadToHeadService:
    @staticmethod
    def get_df(project_slug: str, request: api.HeadToHeadsRequest) -> pd.DataFrame:
        with ProjectService.connect(project_slug) as conn:
            df_h2h = pd.read_sql_query(
                """
                SELECT
                    ra.model_id AS model_a_id,
                    rb.model_id AS model_b_id,
                    ra.prompt AS prompt,
                    ra.id AS response_a_id,
                    rb.id AS response_b_id,
                    ra.response AS response_a,
                    rb.response AS response_b,
                    JSON_GROUP_ARRAY(JSON_OBJECT(
                        'judge_id', j1.id,
                        'judge_name', j1.name,
                        'winner', h1.winner
                    )) AS history_a,
                    JSON_GROUP_ARRAY(JSON_OBJECT(
                        'judge_id', j2.id,
                        'judge_name', j2.name,
                        'winner', invert_winner(h2.winner)
                    )) AS history_b
                FROM response ra
                JOIN response rb ON ra.prompt = rb.prompt
                JOIN model ma ON ra.model_id = ma.id
                JOIN model mb ON rb.model_id = mb.id
                LEFT JOIN head_to_head h1 ON h1.response_a_id = ra.id AND h1.response_b_id = rb.id
                LEFT JOIN judge j1 ON j1.id = h1.judge_id
                LEFT JOIN head_to_head h2 ON h2.response_b_id = ra.id AND h2.response_a_id = rb.id
                LEFT JOIN judge j2 ON j2.id = h2.judge_id
                WHERE ra.model_id = :model_a_id
                AND (:model_b_id IS NULL OR rb.model_id = :model_b_id)
                AND ra.model_id != rb.model_id
                GROUP BY ra.model_id, rb.model_id, ra.id, rb.id, ra.prompt, ra.response, rb.response
                ORDER BY ra.id, rb.id
                """,
                conn,
                params=dict(model_a_id=request.model_a_id, model_b_id=request.model_b_id),
            )
        if len(df_h2h) == 0:
            df_h2h = df_h2h.assign(history=None)
        else:
            df_h2h["history"] = df_h2h.apply(
                lambda r: [
                    h for h in [*json.loads(r.history_a), *json.loads(r.history_b)] if h["judge_id"] is not None
                ],
                axis=1,
            )
        return df_h2h.drop(columns=["history_a", "history_b"])

    @staticmethod
    def get(project_slug: str, request: api.HeadToHeadsRequest) -> list[api.HeadToHead]:
        df_h2h = HeadToHeadService.get_df(project_slug, request)
        return [
            api.HeadToHead(
                prompt=r.prompt,
                response_a_id=r.response_a_id,
                response_a=r.response_a,
                response_b_id=r.response_b_id,
                response_b=r.response_b,
                history=[api.HeadToHeadHistoryItem(**h) for h in r.history],
            )
            for r in df_h2h.itertuples()
        ]

    @staticmethod
    def get_count(project_slug: str) -> int:
        with ProjectService.connect(project_slug) as conn:
            ((n_h2h,),) = conn.execute(
                """
                SELECT COUNT(1) / 2
                FROM response ra
                JOIN response rb ON ra.id != rb.id AND ra.prompt = rb.prompt AND ra.model_id != rb.model_id
                """,
            ).fetchall()
        return n_h2h

    @staticmethod
    def submit_vote(project_slug: str, request: api.HeadToHeadVoteRequest) -> None:
        # 1. ensure judge exists
        JudgeService.create_human_judge(project_slug, request.human_judge_name)

        with ProjectService.connect(project_slug, commit=True) as conn:
            cur = conn.cursor()

            # 2. insert head-to-head record
            cur.execute(
                """
                INSERT INTO head_to_head (response_id_slug, response_a_id, response_b_id, judge_id, winner)
                SELECT :response_id_slug, :response_a_id, :response_b_id, j.id, :winner
                FROM judge j
                WHERE j.name = :judge_name
                ON CONFLICT (response_id_slug, judge_id) DO UPDATE SET
                    winner = IIF(response_a_id = :response_b_id, invert_winner(EXCLUDED.winner), EXCLUDED.winner)
            """,
                dict(
                    **dataclasses.asdict(request),
                    response_id_slug=id_slug(request.response_a_id, request.response_b_id),
                    judge_name=request.human_judge_name,
                ),
            )

            # 3. adjust elo scores
            df_model = pd.read_sql_query(
                """
                SELECT id, elo
                FROM model m
                WHERE EXISTS (SELECT 1 FROM response r WHERE r.id = :response_a_id AND r.model_id = m.id)
                UNION ALL
                SELECT id, elo
                FROM model m
                WHERE EXISTS (SELECT 1 FROM response r WHERE r.id = :response_b_id AND r.model_id = m.id)
                """,
                conn,
                params=dict(response_a_id=request.response_a_id, response_b_id=request.response_b_id),
            )
            model_a = df_model.iloc[0]
            model_b = df_model.iloc[1]
            elo_a, elo_b = EloService.compute_elo_single(model_a.elo, model_b.elo, request.winner)
            for model_id, elo in [(model_a.id, elo_a), (model_b.id, elo_b)]:
                cur.execute("UPDATE model SET elo = :elo WHERE id = :model_id", dict(model_id=model_id, elo=elo))

    @staticmethod
    def upload_head_to_heads(project_slug: str, df_h2h: pd.DataFrame) -> None:  # TODO: return type?
        try:
            check_required_columns(df_h2h, ["response_a_id", "response_b_id", "judge_id", "winner"])
        except ValueError as e:
            raise BadRequestError(str(e))
        df_h2h_deduped = df_h2h.copy()
        df_h2h_deduped["response_id_slug"] = df_h2h_deduped.apply(
            lambda r: id_slug(r.response_a_id, r.response_b_id), axis=1
        )
        df_h2h_deduped = df_h2h_deduped.drop_duplicates(subset=["response_id_slug", "judge_id"], keep="first")
        if len(df_h2h_deduped) != len(df_h2h):
            logger.warning(f"Dropped {len(df_h2h) - len(df_h2h_deduped)} duplicate rows before uploading")
        with ProjectService.connect(project_slug, commit=True) as conn:
            with temporary_table(conn, df_h2h_deduped) as tmp:
                conn.execute(f"""
                    INSERT INTO head_to_head (response_id_slug, response_a_id, response_b_id, judge_id, winner)
                    SELECT response_id_slug, response_a_id, response_b_id, judge_id, winner
                    FROM {tmp}
                    WHERE TRUE
                    ON CONFLICT (response_id_slug, judge_id) DO UPDATE SET
                        winner = IIF(
                            response_a_id = EXCLUDED.response_a_id,
                            EXCLUDED.winner,
                            invert_winner(EXCLUDED.winner)
                        )
                """)
