import time
from collections import defaultdict
from typing import Literal

import pandas as pd
from pydantic.dataclasses import dataclass
from loguru import logger

from autoarena.service.project import ProjectService


@dataclass(frozen=True)
class EloConfig:
    default_score: float = 1_000
    k: int = 4
    scale: int = 400
    base: int = 10


DEFAULT_ELO_CONFIG = EloConfig()


class EloService:
    @staticmethod
    def get_df_head_to_head(project_slug: str) -> pd.DataFrame:
        with ProjectService.connect(project_slug) as conn:
            return conn.execute(
                """
                SELECT
                    j.id AS judge_id,
                    j.name AS judge_name,
                    ma.id AS model_a_id,
                    ma.name AS model_a,
                    mb.id AS model_b_id,
                    mb.name AS model_b,
                    h.winner
                FROM head_to_head h
                JOIN judge j ON h.judge_id = j.id
                JOIN response ra ON h.response_a_id = ra.id
                JOIN response rb ON h.response_b_id = rb.id
                JOIN model ma ON ra.model_id = ma.id
                JOIN model mb ON rb.model_id = mb.id
                ORDER BY h.id -- ensure we are replaying head-to-heads in the order they were submitted
            """,
            ).df()

    @staticmethod
    def reseed_scores(project_slug: str) -> None:
        df_h2h = EloService.get_df_head_to_head(project_slug)
        df_elo = EloService.compute_elo(df_h2h)  # noqa: F841
        with ProjectService.connect(project_slug) as conn:
            conn.execute(  # reset all scores before updating new ones
                "UPDATE model SET elo = $default_elo, q025 = NULL, q975 = NULL",
                dict(default_elo=EloConfig.default_score),
            )
            conn.execute(
                """
                INSERT INTO model (name, elo, q025, q975)
                SELECT model, elo, q025, q975
                FROM df_elo
                ON CONFLICT (name) DO UPDATE SET
                    elo = EXCLUDED.elo,
                    q025 = EXCLUDED.q025,
                    q975 = EXCLUDED.q975;
            """,
            )

    # most elo-related code is from https://github.com/lm-sys/FastChat/blob/main/fastchat/serve/monitor/elo_analysis.py
    @staticmethod
    def compute_elo_single(
        elo_a: float,
        elo_b: float,
        winner: Literal["A", "B", "-"],
        config: EloConfig = DEFAULT_ELO_CONFIG,
    ) -> tuple[float, float]:
        expected_a = 1 / (1 + config.base ** ((elo_b - elo_a) / config.scale))
        expected_b = 1 / (1 + config.base ** ((elo_a - elo_b) / config.scale))
        score_a = 1 if winner == "A" else 0 if winner == "B" else 0.5
        elo_a += config.k * (score_a - expected_a)
        elo_b += config.k * (1 - score_a - expected_b)
        return elo_a, elo_b

    @staticmethod
    def compute_elo(df_h2h: pd.DataFrame, *, config: EloConfig = DEFAULT_ELO_CONFIG) -> pd.DataFrame:
        df_elo = EloService._compute_elo_once(df_h2h, config=config)
        df_elo = EloService._compute_confidence_intervals(df_elo, df_h2h, config=config)
        return df_elo

    @staticmethod
    def _compute_confidence_intervals(
        df_elo: pd.DataFrame,
        df_h2h: pd.DataFrame,
        *,
        config: EloConfig = DEFAULT_ELO_CONFIG,
    ) -> pd.DataFrame:
        df_bootstrap = EloService._get_bootstrap_result(df_h2h, num_rounds=200, config=config)
        # set Elo score to the median of the bootstrap result -- the order of the head-to-heads doesn't matter for bulk
        #  judging so the "true" score is in the middle of the differently ordered rollouts
        df_elo = df_elo.merge(df_bootstrap.quantile(0.5).rename("elo_median"), left_on="model", right_index=True)
        df_elo["elo"] = df_elo["elo_median"]
        df_elo = df_elo.merge(df_bootstrap.quantile(0.025).rename("q025"), left_on="model", right_index=True)
        df_elo = df_elo.merge(df_bootstrap.quantile(0.975).rename("q975"), left_on="model", right_index=True)
        df_elo["ci95"] = df_elo["q975"] - df_elo["q025"]
        return df_elo[["model", "elo", "q025", "q975", "ci95"]]

    @staticmethod
    def _compute_elo_once(df_h2h: pd.DataFrame, *, config: EloConfig = DEFAULT_ELO_CONFIG) -> pd.DataFrame:
        rating: dict[str, float] = defaultdict(lambda: config.default_score)
        for _, model_a, model_b, winner in df_h2h[["model_a", "model_b", "winner"]].itertuples():
            elo_a, elo_b = EloService.compute_elo_single(rating[model_a], rating[model_b], winner, config=config)
            rating[model_a] = elo_a
            rating[model_b] = elo_b
        df_elo = pd.DataFrame(dict(rating).items(), columns=["model", "elo"])
        return df_elo.sort_values(by="elo", ascending=False)

    @staticmethod
    def _get_bootstrap_result(
        df_h2h: pd.DataFrame,
        *,
        num_rounds: int = 1_000,
        config: EloConfig = DEFAULT_ELO_CONFIG,
    ) -> pd.DataFrame:
        rows = []
        t_start = time.time()
        logger.info(f"Bootstrapping confidence intervals with {num_rounds} rounds...")
        for _ in range(num_rounds):
            df_h2h_tmp = df_h2h.sample(frac=1.0, replace=True)
            rows.append(EloService._compute_elo_once(df_h2h_tmp, config=config))
        logger.info(f"Bootstrapped confidence intervals in {time.time() - t_start:0.1f} seconds")
        df = pd.DataFrame([{r.model: r.elo for r in df_row.itertuples()} for df_row in rows])
        return df[df.median().sort_values(ascending=False).index]
