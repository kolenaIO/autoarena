import dataclasses

from autostack.api import api
from autostack.elo import compute_elo_single
from autostack.judge.human import HumanJudge
from autostack.store.database import get_database_connection


class HeadToHeadService:
    @staticmethod
    def get(request: api.HeadToHeadsRequest) -> list[api.HeadToHead]:
        with get_database_connection() as conn:
            df_h2h = conn.execute(
                """
                SELECT
                    ra.id AS result_a_id,
                    rb.id AS result_b_id,
                    ra.prompt AS prompt,
                    ra.response AS response_a,
                    rb.response AS response_b
                FROM result ra
                JOIN result rb ON ra.prompt = rb.prompt
                WHERE ra.model_id = $model_a_id
                AND rb.model_id = $model_b_id
            """,
                dict(model_a_id=request.model_a_id, model_b_id=request.model_b_id),
            ).df()
        return [api.HeadToHead(**r) for _, r in df_h2h.iterrows()]

    # TODO: naming is weird -- 'judgement', 'rating', 'vote', 'battle' all used
    @staticmethod
    def submit_judgement(request: api.HeadToHeadJudgementRequest) -> None:
        with get_database_connection() as conn:
            # 1. insert battle record
            human_judge = HumanJudge()
            conn.execute(
                """
                INSERT INTO battle (result_a_id, result_b_id, judge_id, winner)
                SELECT $result_a_id, $result_b_id, j.id, $winner
                FROM judge j
                WHERE j.project_id = $project_id
                AND j.name = $judge_name
                ON CONFLICT (result_a_id, result_b_id, judge_id) DO UPDATE SET winner = EXCLUDED.winner
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
            elo_a, elo_b = compute_elo_single(model_a.elo, model_b.elo, request.winner)
            for model_id, elo in [(model_a.id, elo_a), (model_b.id, elo_b)]:
                conn.execute("UPDATE model SET elo = $elo WHERE id = $model_id", dict(model_id=model_id, elo=elo))
