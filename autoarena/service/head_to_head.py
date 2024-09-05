import dataclasses

import pandas as pd

from autoarena.api import api
from autoarena.service.elo import EloService
from autoarena.judge.human import HumanJudge
from autoarena.store.database import get_database_connection


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
                            'winner': b1.winner,
                        }) FILTER (b1.winner IS NOT NULL),
                        ARRAY_AGG({
                            'judge_id': j2.id,
                            'judge_name': j2.name,
                            'winner': CASE WHEN b2.winner = 'A' THEN 'B'
                                           WHEN b2.winner = 'B' THEN 'A'
                                           ELSE b2.winner END,
                        }) FILTER (b2.winner IS NOT NULL)
                    ), []) AS history
                FROM result ra
                JOIN result rb ON ra.prompt = rb.prompt
                JOIN model ma ON ra.model_id = ma.id
                JOIN model mb ON rb.model_id = mb.id
                LEFT JOIN battle b1 ON b1.result_a_id = ra.id AND b1.result_b_id = rb.id
                LEFT JOIN judge j1 ON j1.id = b1.judge_id
                LEFT JOIN battle b2 ON b2.result_b_id = ra.id AND b2.result_a_id = rb.id
                LEFT JOIN judge j2 ON j2.id = b2.judge_id
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

    # TODO: naming is weird -- 'judgement', 'rating', 'vote', 'battle' all used
    @staticmethod
    def submit_judgement(request: api.HeadToHeadJudgementRequest) -> None:
        with get_database_connection() as conn:
            # 1. insert battle record
            human_judge = HumanJudge()
            conn.execute(
                """
                INSERT INTO battle (result_id_slug, result_a_id, result_b_id, judge_id, winner)
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
