import time
from collections import defaultdict

import pandas as pd
from pydantic.dataclasses import dataclass
from loguru import logger

from autoarena.api import api
from autoarena.service.project import ProjectService


@dataclass(frozen=True)
class EloConfig:
    default_score: float = 1_000
    k: int = 4
    scale: int = 400
    base: int = 10
    n_bootstrap_rounds: int = 200


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
    def reseed_scores(project_slug: str, config: EloConfig = DEFAULT_ELO_CONFIG) -> None:
        df_h2h = EloService.get_df_head_to_head(project_slug)
        df_elo = EloService.compute_elo(df_h2h, config=config)  # noqa: F841
        with ProjectService.connect(project_slug) as conn:
            conn.execute(
                """
                UPDATE model
                SET elo = IFNULL(df_elo.elo, $default_elo), q025 = df_elo.q025, q975 = df_elo.q975
                FROM model m2
                LEFT JOIN df_elo ON df_elo.model = m2.name -- left join to set null values for any models without votes
                WHERE model.id = m2.id;
                """,
                dict(default_elo=config.default_score),
            )

    # most elo-related code is from https://github.com/lm-sys/FastChat/blob/main/fastchat/serve/monitor/elo_analysis.py
    @staticmethod
    def compute_elo_single(
        elo_a: float,
        elo_b: float,
        winner: api.WinnerType,
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
        df_bootstrap = EloService._get_bootstrap_result(df_h2h, config=config)
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
    def _get_bootstrap_result(df_h2h: pd.DataFrame, *, config: EloConfig = DEFAULT_ELO_CONFIG) -> pd.DataFrame:
        rows = []
        t_start = time.time()
        logger.info(f"Bootstrapping confidence intervals with {config.n_bootstrap_rounds} rounds...")
        for _ in range(config.n_bootstrap_rounds):
            df_h2h_tmp = df_h2h.sample(frac=1.0, replace=True)
            rows.append(EloService._compute_elo_once(df_h2h_tmp, config=config))
        logger.info(f"Bootstrapped confidence intervals in {time.time() - t_start:0.1f} seconds")
        df = pd.DataFrame([{r.model: r.elo for r in df_row.itertuples()} for df_row in rows])
        return df[df.median().sort_values(ascending=False).index]
