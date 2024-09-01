from autostack.elo import compute_elo, add_rank_and_confidence_intervals
from autostack.store.database import get_database_connection


class EloService:
    DEFAULT_ELO_SCORE = 1_000  # TODO: use this elsewhere

    @staticmethod
    def reseed_scores(project_id: int) -> None:
        with get_database_connection() as conn:
            df_battle = conn.execute(
                """
                SELECT ma.name AS model_a, mb.name AS model_b, b.winner
                FROM battle b
                JOIN result ra ON b.result_a_id = ra.id
                JOIN result rb ON b.result_b_id = rb.id
                JOIN model ma ON ra.model_id = ma.id
                JOIN model mb ON rb.model_id = mb.id
                WHERE ma.project_id = $project_id
                AND mb.project_id = $project_id
            """,
                dict(project_id=project_id),
            ).df()
        df_elo = compute_elo(df_battle)
        df_elo = add_rank_and_confidence_intervals(df_elo, df_battle)
        with get_database_connection() as conn:
            conn.execute(  # reset all scores before updating new ones
                "UPDATE model SET elo = $default_elo, q025 = NULL, q975 = NULL WHERE project_id = $project_id",
                dict(project_id=project_id, default_elo=EloService.DEFAULT_ELO_SCORE),
            )
            conn.execute(
                """
                INSERT INTO model (project_id, name, elo, q025, q975)
                SELECT $project_id, model, elo, q025, q975
                FROM df_elo
                ON CONFLICT (project_id, name) DO UPDATE SET
                    elo = EXCLUDED.elo,
                    q025 = EXCLUDED.q025,
                    q975 = EXCLUDED.q975;
            """,
                dict(project_id=project_id),
            )
