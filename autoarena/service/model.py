import numpy as np
import pandas as pd

from autoarena.api import api
from autoarena.error import NotFoundError
from autoarena.service.elo import EloService, DEFAULT_ELO_CONFIG
from autoarena.store.database import get_database_connection


class ModelService:
    MODELS_QUERY = """
        WITH datapoint_count AS (
            SELECT r.model_id, COUNT(1) AS datapoint_count
            FROM result r
            GROUP BY r.model_id
        ), vote_count_a AS ( -- TODO: this is inelegant but this query is tricky to write
            SELECT m.id AS model_id, SUM(IF(b.id IS NOT NULL, 1, 0)) AS vote_count
            FROM model m
            JOIN result r ON r.model_id = m.id
            LEFT JOIN battle b ON r.id = b.result_a_id
            GROUP BY m.id
        ), vote_count_b AS (
            SELECT m.id AS model_id, SUM(IF(b.id IS NOT NULL, 1, 0)) AS vote_count
            FROM model m
            JOIN result r ON r.model_id = m.id
            LEFT JOIN battle b ON r.id = b.result_b_id
            GROUP BY m.id
        )
        SELECT
            id,
            name,
            created,
            elo,
            q025,
            q975,
            IFNULL(dc.datapoint_count, 0) AS datapoints,
            IFNULL(vca.vote_count, 0) + IFNULL(vcb.vote_count, 0) AS votes
        FROM model m
        LEFT JOIN datapoint_count dc ON m.id = dc.model_id
        LEFT JOIN vote_count_a vca ON m.id = vca.model_id
        LEFT JOIN vote_count_b vcb ON m.id = vcb.model_id
        """

    @staticmethod
    def get_by_id(model_id: int) -> api.Model:
        with get_database_connection() as conn:
            df_model = conn.execute(f"{ModelService.MODELS_QUERY} WHERE m.id = $model_id", dict(model_id=model_id)).df()
        try:
            return [api.Model(**r) for _, r in df_model.iterrows()][0]
        except IndexError:
            raise NotFoundError(f"Model with ID '{model_id}' not found")

    @staticmethod
    def get_project_id(model_id: int) -> int:
        try:
            with get_database_connection() as conn:
                params = dict(model_id=model_id)
                ((project_id,),) = conn.execute("SELECT project_id FROM model WHERE id = $model_id", params).fetchall()
            return project_id
        except ValueError:
            raise NotFoundError(f"Model with ID '{model_id}' not found")

    @staticmethod
    def get_all_df(project_id: int) -> pd.DataFrame:
        with get_database_connection() as conn:
            df_model = conn.execute(
                f"{ModelService.MODELS_QUERY} WHERE m.project_id = $project_id",
                dict(project_id=project_id),
            ).df()
        df_model = df_model.replace({np.nan: None})
        return df_model

    @staticmethod
    def get_all(project_id: int) -> list[api.Model]:
        df_model = ModelService.get_all_df(project_id)
        return [api.Model(**r) for _, r in df_model.iterrows()]

    @staticmethod
    def get_all_ranked_by_judge(project_id: int, judge_id: int) -> list[api.Model]:
        df_h2h = EloService.get_df_head_to_head(project_id)
        df_h2h = df_h2h[df_h2h["judge_id"] == judge_id]
        df_elo = EloService.compute_elo(df_h2h)
        df_elo = EloService.compute_confidence_intervals(df_elo, df_h2h)  # TODO: is this too expensive?
        df_model = ModelService.get_all_df(project_id)
        df_out = pd.merge(df_model, df_elo, left_on="name", right_on="model", how="left")
        df_out[["elo", "q025", "q975"]] = df_out[["elo_y", "q025_y", "q975_y"]]
        df_out["elo"] = df_out["elo"].replace({np.nan: DEFAULT_ELO_CONFIG.default_score})
        df_out = df_out.replace({np.nan: None})
        votes_a, votes_b = df_h2h.model_a_id.value_counts(), df_h2h.model_b_id.value_counts()
        df_votes = pd.merge(votes_a, votes_b, left_index=True, right_index=True, how="outer")
        df_votes = df_votes.replace({np.nan: 0})
        df_votes["votes"] = df_votes["count_x"] + df_votes["count_y"]
        df_out = df_out.merge(df_votes, left_on="id", right_index=True, how="left")
        df_out["votes"] = df_out["votes_y"].replace({np.nan: 0})
        df_out = df_out[["id", "name", "created", "elo", "q025", "q975", "datapoints", "votes"]]
        return [api.Model(**r) for _, r in df_out.iterrows()]

    @staticmethod
    def upload_results(project_id: int, model_name: str, df_result: pd.DataFrame) -> api.Model:
        with get_database_connection() as conn:
            params = dict(project_id=project_id, model_name=model_name)
            ((new_model_id,),) = conn.execute(
                """
                INSERT INTO model (project_id, name)
                VALUES ($project_id, $model_name)
                RETURNING id
                """,
                params,
            ).fetchall()
            df_result["model_id"] = new_model_id
            conn.execute("""
                INSERT INTO result (model_id, prompt, response)
                SELECT model_id, prompt, response
                FROM df_result
            """)
        models = ModelService.get_all(project_id)
        new_model = [model for model in models if model.id == new_model_id][0]
        return new_model

    @staticmethod
    def delete(model_id: int) -> None:
        params = dict(model_id=model_id)
        with get_database_connection() as conn:
            conn.execute(
                """
                DELETE FROM battle b
                WHERE EXISTS (
                    SELECT 1
                    FROM result r
                    WHERE r.model_id = $model_id
                    AND (b.result_a_id = r.id OR b.result_b_id = r.id)
                )
                """,
                params,
            )
            conn.execute("DELETE FROM result WHERE model_id = $model_id", params)
            conn.execute("DELETE FROM model WHERE id = $model_id", params)

    @staticmethod
    def get_results(model_id: int) -> list[api.ModelResult]:
        df_result = ModelService.get_df_result(model_id)
        return [api.ModelResult(prompt=r.prompt, response=r.response) for r in df_result.itertuples()]

    @staticmethod
    def get_df_result(model_id: int) -> pd.DataFrame:
        with get_database_connection() as conn:
            df_result = conn.execute(
                """
                SELECT
                    m.name AS model,
                    r.prompt AS prompt,
                    r.response AS response
                FROM model m
                JOIN result r ON r.model_id = m.id
                WHERE m.id = $model_id
            """,
                dict(model_id=model_id),
            ).df()
        return df_result

    @staticmethod
    def get_df_head_to_head(model_id: int) -> pd.DataFrame:
        with get_database_connection() as conn:
            df_h2h = conn.execute(
                """
                SELECT
                    ra.prompt,
                    ma.name AS model_a,
                    mb.name AS model_b,
                    ra.response AS response_a,
                    rb.response AS response_b,
                    j.name AS judge,
                    b.winner
                FROM battle b
                JOIN judge j ON b.judge_id = j.id
                JOIN result ra ON ra.id = b.result_a_id
                JOIN result rb ON rb.id = b.result_b_id
                JOIN model ma ON ma.id = ra.model_id
                JOIN model mb ON mb.id = rb.model_id
                WHERE ma.id = $model_id
                OR mb.id = $model_id
            """,
                dict(model_id=model_id),
            ).df()
        return df_h2h

    # TODO: should add tests for tricky logic like this
    @staticmethod
    def get_head_to_head_stats(model_id: int) -> list[api.ModelHeadToHeadStats]:
        with get_database_connection() as conn:
            df_h2h_stats = conn.execute(
                """
                WITH battle_result AS (
                    SELECT
                        ra.model_id,
                        rb.model_id AS other_model_id,
                        b.judge_id,
                        CASE WHEN b.winner = 'A' THEN TRUE WHEN b.winner = 'B' THEN FALSE END AS won
                    FROM battle b
                    JOIN result ra ON ra.id = b.result_a_id
                    JOIN result rb ON rb.id = b.result_b_id
                    UNION ALL
                    SELECT
                        rb.model_id,
                        ra.model_id AS other_model_id,
                        b.judge_id,
                        CASE WHEN b.winner = 'B' THEN TRUE WHEN b.winner = 'A' THEN FALSE END AS won
                    FROM battle b
                    JOIN result ra ON ra.id = b.result_a_id
                    JOIN result rb ON rb.id = b.result_b_id
                )
                SELECT
                    m_other.id AS other_model_id,
                    m_other.name AS other_model_name,
                    j.id AS judge_id,
                    j.name AS judge_name,
                    SUM(IF(br.won IS TRUE, 1, 0)) AS count_wins,
                    SUM(IF(br.won IS FALSE, 1, 0)) AS count_losses,
                    SUM(IF(br.won IS NULL, 1, 0)) AS count_ties
                FROM battle_result br
                JOIN judge j ON j.id = br.judge_id
                JOIN model m ON m.id = br.model_id
                JOIN model m_other ON m_other.id = br.other_model_id
                WHERE m.id = $model_id
                GROUP BY m.id, m.name, m_other.id, m_other.name, j.id, j.name
            """,
                dict(model_id=model_id),
            ).df()
        return [api.ModelHeadToHeadStats(**r) for _, r in df_h2h_stats.iterrows()]
