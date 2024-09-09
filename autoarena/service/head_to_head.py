import dataclasses

import pandas as pd
from loguru import logger

from autoarena.api import api
from autoarena.service.elo import EloService
from autoarena.judge.human import HumanJudge
from autoarena.store.database import get_database_connection
from autoarena.store.utils import id_slug


class HeadToHeadService:
    @staticmethod
    def get_df(request: api.HeadToHeadsRequest) -> pd.DataFrame:
        with get_database_connection() as conn:
            return conn.execute(
                """
                SELECT
                    ra.model_id AS model_a_id,
                    rb.model_id AS model_b_id,
                    ra.id AS result_a_id,
                    rb.id AS result_b_id,
                    ra.prompt AS prompt,
                    ra.response AS response_a,
                    rb.response AS response_b,
                    IFNULL(ARRAY_CONCAT(
                        ARRAY_AGG({
                            'judge_id': j1.id,
                            'judge_name': j1.name,
                            'winner': h1.winner,
                        }) FILTER (h1.winner IS NOT NULL),
                        ARRAY_AGG({
                            'judge_id': j2.id,
                            'judge_name': j2.name,
                            'winner': CASE WHEN h2.winner = 'A' THEN 'B'
                                           WHEN h2.winner = 'B' THEN 'A'
                                           ELSE h2.winner END,
                        }) FILTER (h2.winner IS NOT NULL)
                    ), []) AS history
                FROM result ra
                JOIN result rb ON ra.prompt = rb.prompt
                JOIN model ma ON ra.model_id = ma.id
                JOIN model mb ON rb.model_id = mb.id
                LEFT JOIN head_to_head h1 ON h1.result_a_id = ra.id AND h1.result_b_id = rb.id
                LEFT JOIN judge j1 ON j1.id = h1.judge_id
                LEFT JOIN head_to_head h2 ON h2.result_b_id = ra.id AND h2.result_a_id = rb.id
                LEFT JOIN judge j2 ON j2.id = h2.judge_id
                WHERE ra.model_id = $model_a_id
                AND ($model_b_id IS NULL OR rb.model_id = $model_b_id)
                AND ra.model_id != rb.model_id
                AND ma.project_id = mb.project_id
                GROUP BY ra.model_id, rb.model_id, ra.id, rb.id, ra.prompt, ra.response, rb.response
                ORDER BY ra.id, rb.id
                """,
                dict(model_a_id=request.model_a_id, model_b_id=request.model_b_id),
            ).df()

    @staticmethod
    def get(request: api.HeadToHeadsRequest) -> list[api.HeadToHead]:
        df_h2h = HeadToHeadService.get_df(request)
        return [
            api.HeadToHead(
                prompt=r.prompt,
                result_a_id=r.result_a_id,
                response_a=r.response_a,
                result_b_id=r.result_b_id,
                response_b=r.response_b,
                history=[api.HeadToHeadHistoryItem(**h) for h in r.history],
            )
            for r in df_h2h.itertuples()
        ]

    @staticmethod
    def submit_judgement(request: api.HeadToHeadJudgementRequest) -> None:
        with get_database_connection() as conn:
            # 1. insert head-to-head record
            human_judge = HumanJudge()
            conn.execute(
                """
                INSERT INTO head_to_head (result_id_slug, result_a_id, result_b_id, judge_id, winner)
                SELECT id_slug($result_a_id, $result_b_id), $result_a_id, $result_b_id, j.id, $winner
                FROM judge j
                WHERE j.project_id = $project_id
                AND j.name = $judge_name
                ON CONFLICT (result_id_slug, judge_id) DO UPDATE SET
                    winner = IF(result_a_id = $result_b_id, invert_winner(EXCLUDED.winner), EXCLUDED.winner)
            """,
                dict(**dataclasses.asdict(request), judge_name=human_judge.name),
            )

            # 2. adjust elo scores
            df_model = conn.execute(
                """
                SELECT id, elo
                FROM model m
                WHERE EXISTS (SELECT 1 FROM result r WHERE r.id = $result_a_id AND r.model_id = m.id)
                UNION ALL
                SELECT id, elo
                FROM model m
                WHERE EXISTS (SELECT 1 FROM result r WHERE r.id = $result_b_id AND r.model_id = m.id)
            """,
                dict(result_a_id=request.result_a_id, result_b_id=request.result_b_id),
            ).df()
            model_a = df_model.iloc[0]
            model_b = df_model.iloc[1]
            elo_a, elo_b = EloService.compute_elo_single(model_a.elo, model_b.elo, request.winner)
            for model_id, elo in [(model_a.id, elo_a), (model_b.id, elo_b)]:
                conn.execute("UPDATE model SET elo = $elo WHERE id = $model_id", dict(model_id=model_id, elo=elo))

    @staticmethod
    def upload_head_to_heads(df_h2h: pd.DataFrame) -> None:  # TODO: return type?
        required_columns = {"result_a_id", "result_b_id", "judge_id", "winner"}
        missing_columns = required_columns - set(df_h2h.columns)
        if len(missing_columns) > 0:
            raise ValueError(f"missing required column(s): {missing_columns}")
        df_h2h_deduped = df_h2h.copy()
        df_h2h_deduped["result_id_slug"] = df_h2h_deduped.apply(lambda r: id_slug(r.result_a_id, r.result_b_id), axis=1)
        df_h2h_deduped = df_h2h_deduped.drop_duplicates(subset=["result_id_slug"], keep="first")
        if len(df_h2h_deduped) != len(df_h2h):
            logger.warning(f"Dropped {len(df_h2h) - len(df_h2h_deduped)} duplicate rows before uploading")
        with get_database_connection() as conn:
            conn.execute("""
                INSERT INTO head_to_head (result_id_slug, result_a_id, result_b_id, judge_id, winner)
                SELECT id_slug(result_a_id, result_b_id), result_a_id, result_b_id, judge_id, winner
                FROM df_h2h_deduped
                ON CONFLICT (result_id_slug, judge_id) DO UPDATE SET winner = EXCLUDED.winner
            """)
