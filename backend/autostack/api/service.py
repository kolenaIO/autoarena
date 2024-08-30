import functools
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from tqdm import tqdm

from autostack.store.database import get_df_battle


@dataclass(frozen=True)
class Model:
    id: int
    name: str
    created: datetime
    elo: float
    q025: float
    q975: float
    votes: int


# most elo-related code is from https://github.com/lm-sys/FastChat/blob/main/fastchat/serve/monitor/elo_analysis.py
def compute_elo(
    df_battles: pd.DataFrame,
    k: int = 4,
    scale: int = 400,
    base: int = 10,
    init_rating: int = 1_000,
) -> pd.DataFrame:
    rating: dict[str, float] = defaultdict(lambda: init_rating)
    for _, model_a, model_b, winner in df_battles[["model_a_name", "model_b_name", "winner"]].itertuples():
        rating_a = rating[model_a]
        rating_b = rating[model_b]
        expected_a = 1 / (1 + base ** ((rating_b - rating_a) / scale))
        expected_b = 1 / (1 + base ** ((rating_a - rating_b) / scale))
        score_a = 1 if winner == "A" else 0 if winner == "B" else 0.5
        rating[model_a] += k * (score_a - expected_a)
        rating[model_b] += k * (1 - score_a - expected_b)
    df_elos = pd.DataFrame(dict(rating).items(), columns=["model", "elo"])
    return df_elos.sort_values(by="elo", ascending=False)


def get_bootstrap_result(df_battles: pd.DataFrame, num_round: int = 1_000) -> pd.DataFrame:
    rows = []
    for _ in tqdm(range(num_round), desc="bootstrap"):
        tmp_battles = df_battles.sample(frac=1.0, replace=True)
        rows.append(compute_elo(tmp_battles))
    df = pd.DataFrame([{r.model: r.elo for r in df_row.itertuples()} for df_row in rows])
    return df[df.median().sort_values(ascending=False).index]


def add_rank_and_confidence_intervals(df_elos: pd.DataFrame, df_battles: pd.DataFrame) -> pd.DataFrame:
    df_elos["rank"] = df_elos["elo"].rank(ascending=False).astype(int)
    battle_counts = df_battles["model_a_name"].value_counts() + df_battles["model_b_name"].value_counts()
    df_elos = df_elos.merge(battle_counts, left_on="model", right_index=True)
    df_bootstrap = get_bootstrap_result(df_battles, num_round=100)  # TODO: should precompute this
    df_elos = df_elos.merge(df_bootstrap.quantile(0.025).rename("q025"), left_on="model", right_index=True)
    df_elos = df_elos.merge(df_bootstrap.quantile(0.975).rename("q975"), left_on="model", right_index=True)
    # TODO: should we be doing this? fudge to ensure that elo isn't outside of CI
    df_elos["elo"] = df_elos.apply(lambda r: max(r.q025, min(r.elo, r.q975)), axis=1)
    df_elos["ci95"] = df_elos["q975"] - df_elos["q025"]
    return df_elos


@functools.lru_cache(maxsize=1)
def compute_all_model_elos(project_id: int) -> list[Model]:
    df_battle = get_df_battle(project_id)
    df_elo = compute_elo(df_battle)
    df_elo = add_rank_and_confidence_intervals(df_elo, df_battle)
    return [
        Model(
            id=int(r.rank),  # TODO: shouldn't use rank as ID...
            name=r.model,
            created=datetime.utcnow(),  # r.created, TODO
            elo=r.elo,
            q025=r.q025,
            q975=r.q975,
            votes=r.count,
        )
        for r in df_elo.itertuples()
    ]
