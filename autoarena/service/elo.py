import time
from collections import defaultdict
from typing import Literal, Optional

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
        df_elo = EloService.compute_elo(df_h2h)
        df_elo = EloService.compute_confidence_intervals(df_elo, df_h2h)
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

    @staticmethod
    def get_history(
        project_slug: str,
        model_id: int,
        judge_id: Optional[int],
        config: EloConfig = DEFAULT_ELO_CONFIG,
    ) -> list[api.EloHistoryItem]:
        df_h2h = EloService.get_df_head_to_head(project_slug)
        if judge_id is not None:
            df_h2h = df_h2h[df_h2h["judge_id"] == judge_id]
        rating: dict[int, float] = defaultdict(lambda: config.default_score)
        history: list[api.EloHistoryItem] = []
        for r in df_h2h.itertuples():
            id_a, id_b = r.model_a_id, r.model_b_id
            elo_a, elo_b = EloService.compute_elo_single(rating[id_a], rating[id_b], r.winner, config=config)
            rating[id_a] = elo_a
            rating[id_b] = elo_b
            kw = dict(judge_id=r.judge_id, judge_name=r.judge_name)
            if id_a == model_id:
                history.append(api.EloHistoryItem(other_model_id=id_b, other_model_name=r.model_b, elo=elo_a, **kw))
            if id_b == model_id:
                history.append(api.EloHistoryItem(other_model_id=id_a, other_model_name=r.model_a, elo=elo_b, **kw))
        return history

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
    def compute_elo(df_h2h: pd.DataFrame, config: EloConfig = DEFAULT_ELO_CONFIG) -> pd.DataFrame:
        rating: dict[str, float] = defaultdict(lambda: config.default_score)
        for _, model_a, model_b, winner in df_h2h[["model_a", "model_b", "winner"]].itertuples():
            elo_a, elo_b = EloService.compute_elo_single(rating[model_a], rating[model_b], winner, config=config)
            rating[model_a] = elo_a
            rating[model_b] = elo_b
        df_elo = pd.DataFrame(dict(rating).items(), columns=["model", "elo"])
        return df_elo.sort_values(by="elo", ascending=False)

    @staticmethod
    def compute_confidence_intervals(df_elo: pd.DataFrame, df_h2h: pd.DataFrame) -> pd.DataFrame:
        df_bootstrap = EloService._get_bootstrap_result(df_h2h, num_rounds=200)
        df_elo = df_elo.merge(df_bootstrap.quantile(0.025).rename("q025"), left_on="model", right_index=True)
        df_elo = df_elo.merge(df_bootstrap.quantile(0.975).rename("q975"), left_on="model", right_index=True)
        # TODO: should we be doing this? fudge to ensure that elo isn't outside of CI
        df_elo["elo"] = df_elo.apply(lambda r: max(r.q025, min(r.elo, r.q975)), axis=1)
        df_elo["ci95"] = df_elo["q975"] - df_elo["q025"]
        return df_elo

    @staticmethod
    def _get_bootstrap_result(df_h2h: pd.DataFrame, num_rounds: int = 1_000) -> pd.DataFrame:
        rows = []
        t_start = time.time()
        logger.info(f"Bootstrapping confidence intervals with {num_rounds} rounds...")
        for _ in range(num_rounds):
            # TODO: are we sure we want replacement? this means dupes
            df_h2h_tmp = df_h2h.sample(frac=1.0, replace=True)
            rows.append(EloService.compute_elo(df_h2h_tmp))
        logger.info(f"Bootstrapped confidence intervals in {time.time() - t_start:0.1f} seconds")
        df = pd.DataFrame([{r.model: r.elo for r in df_row.itertuples()} for df_row in rows])
        return df[df.median().sort_values(ascending=False).index]
