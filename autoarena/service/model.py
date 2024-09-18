import numpy as np
import pandas as pd
from loguru import logger

from autoarena.api import api
from autoarena.error import NotFoundError, BadRequestError
from autoarena.service.elo import EloService, DEFAULT_ELO_CONFIG
from autoarena.service.project import ProjectService
from autoarena.store.utils import check_required_columns


class ModelService:
    MODELS_QUERY = """
        WITH response_count AS (
            SELECT r.model_id, COUNT(1) AS response_count
            FROM response r
            GROUP BY r.model_id
        ), vote_count_a AS ( -- this is inelegant but this query is tricky to write
            SELECT m.id AS model_id, SUM(IF(h.id IS NOT NULL, 1, 0)) AS vote_count
            FROM model m
            JOIN response r ON r.model_id = m.id
            LEFT JOIN head_to_head h ON r.id = h.response_a_id
            GROUP BY m.id
        ), vote_count_b AS (
            SELECT m.id AS model_id, SUM(IF(h.id IS NOT NULL, 1, 0)) AS vote_count
            FROM model m
            JOIN response r ON r.model_id = m.id
            LEFT JOIN head_to_head h ON r.id = h.response_b_id
            GROUP BY m.id
        )
        SELECT
            id,
            name,
            created,
            elo,
            q025,
            q975,
            IFNULL(rc.response_count, 0) AS n_responses,
            IFNULL(vca.vote_count, 0) + IFNULL(vcb.vote_count, 0) AS n_votes
        FROM model m
        LEFT JOIN response_count rc ON m.id = rc.model_id
        LEFT JOIN vote_count_a vca ON m.id = vca.model_id
        LEFT JOIN vote_count_b vcb ON m.id = vcb.model_id
        """

    @staticmethod
    def get_by_id(project_slug: str, model_id: int) -> api.Model:
        with ProjectService.connect(project_slug) as conn:
            df_model = conn.execute(f"{ModelService.MODELS_QUERY} WHERE m.id = $model_id", dict(model_id=model_id)).df()
        try:
            return [api.Model(**r) for _, r in df_model.iterrows()][0]
        except IndexError:
            raise NotFoundError(f"Model with ID '{model_id}' not found")

    @staticmethod
    def get_all_df(project_slug: str) -> pd.DataFrame:
        with ProjectService.connect(project_slug) as conn:
            df_model = conn.execute(ModelService.MODELS_QUERY).df()
        df_model = df_model.replace({np.nan: None})
        return df_model

    @staticmethod
    def get_all(project_slug: str) -> list[api.Model]:
        df_model = ModelService.get_all_df(project_slug)
        return [api.Model(**r) for _, r in df_model.iterrows()]

    @staticmethod
    def get_all_ranked_by_judge(project_slug: str, judge_id: int) -> list[api.Model]:
        df_h2h = EloService.get_df_head_to_head(project_slug)
        df_h2h = df_h2h[df_h2h["judge_id"] == judge_id]
        df_elo = EloService.compute_elo(df_h2h)
        df_model = ModelService.get_all_df(project_slug)
        df_out = pd.merge(df_model, df_elo, left_on="name", right_on="model", how="left")
        df_out[["elo", "q025", "q975"]] = df_out[["elo_y", "q025_y", "q975_y"]]
        df_out["elo"] = df_out["elo"].replace({np.nan: DEFAULT_ELO_CONFIG.default_score})
        df_out = df_out.replace({np.nan: None})
        votes_a, votes_b = df_h2h.model_a_id.value_counts(), df_h2h.model_b_id.value_counts()
        df_votes = pd.merge(votes_a, votes_b, left_index=True, right_index=True, how="outer")
        df_votes = df_votes.replace({np.nan: 0})
        df_votes["n_votes"] = df_votes["count_x"] + df_votes["count_y"]
        df_out = df_out.merge(df_votes, left_on="id", right_index=True, how="left")
        df_out["n_votes"] = df_out["n_votes_y"].replace({np.nan: 0})
        df_out = df_out[["id", "name", "created", "elo", "q025", "q975", "n_responses", "n_votes"]]
        return [api.Model(**r) for _, r in df_out.iterrows()]

    @staticmethod
    def upload_responses(project_slug: str, model_name: str, df_response: pd.DataFrame) -> api.Model:
        try:
            check_required_columns(df_response, ["prompt", "response"])
        except ValueError as e:
            raise BadRequestError(str(e))
        n_input = len(df_response)
        df_response = df_response.copy().dropna(subset=["prompt", "response"])
        if len(df_response) != n_input:
            logger.warning(f"Dropped {n_input - len(df_response)} responses with empty prompt or response values")
        logger.info(f"Uploading {len(df_response)} responses from model '{model_name}'")
        with ProjectService.connect(project_slug) as conn:
            ((new_model_id,),) = conn.execute(
                "INSERT INTO model (name) VALUES ($model_name) RETURNING id",
                dict(model_name=model_name),
            ).fetchall()
            df_response["model_id"] = new_model_id
            conn.execute("""
                INSERT INTO response (model_id, prompt, response)
                SELECT model_id, prompt, response
                FROM df_response
            """)
        models = ModelService.get_all(project_slug)
        new_model = [model for model in models if model.id == new_model_id][0]
        return new_model

    @staticmethod
    def delete(project_slug: str, model_id: int) -> None:
        params = dict(model_id=model_id)
        with ProjectService.connect(project_slug) as conn:
            conn.execute(
                """
                DELETE FROM head_to_head h
                WHERE EXISTS (
                    SELECT 1
                    FROM response r
                    WHERE r.model_id = $model_id
                    AND (h.response_a_id = r.id OR h.response_b_id = r.id)
                )
                """,
                params,
            )
            conn.execute("DELETE FROM response WHERE model_id = $model_id", params)
            conn.execute("DELETE FROM model WHERE id = $model_id", params)

    @staticmethod
    def get_responses(project_slug: str, model_id: int) -> list[api.ModelResponse]:
        df_response = ModelService.get_df_response(project_slug, model_id)
        return [api.ModelResponse(prompt=r.prompt, response=r.response) for r in df_response.itertuples()]

    @staticmethod
    def get_df_response(project_slug: str, model_id: int) -> pd.DataFrame:
        with ProjectService.connect(project_slug) as conn:
            df_response = conn.execute(
                """
                SELECT
                    m.name AS model,
                    r.id AS response_id,
                    r.prompt AS prompt,
                    r.response AS response
                FROM model m
                JOIN response r ON m.id = r.model_id
                WHERE m.id = $model_id
            """,
                dict(model_id=model_id),
            ).df()
        if len(df_response) == 0:
            raise NotFoundError(f"Model with ID '{model_id}' not found")  # model can't exist without any responses
        return df_response

    @staticmethod
    def get_df_head_to_head(project_slug: str, model_id: int) -> pd.DataFrame:
        with ProjectService.connect(project_slug) as conn:
            df_h2h = conn.execute(
                """
                SELECT
                    ra.prompt,
                    ma.name AS model_a,
                    mb.name AS model_b,
                    ra.response AS response_a,
                    rb.response AS response_b,
                    j.name AS judge,
                    h.winner
                FROM head_to_head h
                JOIN judge j ON h.judge_id = j.id
                JOIN response ra ON ra.id = h.response_a_id
                JOIN response rb ON rb.id = h.response_b_id
                JOIN model ma ON ma.id = ra.model_id
                JOIN model mb ON mb.id = rb.model_id
                WHERE ma.id = $model_id
                OR mb.id = $model_id
            """,
                dict(model_id=model_id),
            ).df()
        return df_h2h

    @staticmethod
    def get_head_to_head_stats(project_slug: str, model_id: int) -> list[api.ModelHeadToHeadStats]:
        with ProjectService.connect(project_slug) as conn:
            df_h2h_stats = conn.execute(
                """
                WITH head_to_head_response AS (
                    SELECT
                        ra.model_id,
                        rb.model_id AS other_model_id,
                        h.judge_id,
                        CASE WHEN h.winner = 'A' THEN TRUE WHEN h.winner = 'B' THEN FALSE END AS won
                    FROM head_to_head h
                    JOIN response ra ON ra.id = h.response_a_id
                    JOIN response rb ON rb.id = h.response_b_id
                    UNION ALL
                    SELECT
                        rb.model_id,
                        ra.model_id AS other_model_id,
                        h.judge_id,
                        CASE WHEN h.winner = 'B' THEN TRUE WHEN h.winner = 'A' THEN FALSE END AS won
                    FROM head_to_head h
                    JOIN response ra ON ra.id = h.response_a_id
                    JOIN response rb ON rb.id = h.response_b_id
                )
                SELECT
                    m_other.id AS other_model_id,
                    m_other.name AS other_model_name,
                    j.id AS judge_id,
                    j.name AS judge_name,
                    SUM(IF(hr.won IS TRUE, 1, 0)) AS count_wins,
                    SUM(IF(hr.won IS FALSE, 1, 0)) AS count_losses,
                    SUM(IF(hr.won IS NULL, 1, 0)) AS count_ties
                FROM head_to_head_response hr
                JOIN judge j ON j.id = hr.judge_id
                JOIN model m ON m.id = hr.model_id
                JOIN model m_other ON m_other.id = hr.other_model_id
                WHERE m.id = $model_id
                GROUP BY m.id, m.name, m_other.id, m_other.name, j.id, j.name
            """,
                dict(model_id=model_id),
            ).df()
        return [api.ModelHeadToHeadStats(**r) for _, r in df_h2h_stats.iterrows()]
