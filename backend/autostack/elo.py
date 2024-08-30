from collections import defaultdict

import pandas as pd
from tqdm import tqdm


# most elo-related code is from https://github.com/lm-sys/FastChat/blob/main/fastchat/serve/monitor/elo_analysis.py
def compute_elo(
    df_battles: pd.DataFrame,
    k: int = 4,
    scale: int = 400,
    base: int = 10,
    init_rating: int = 1_000,
) -> pd.DataFrame:
    rating: dict[str, float] = defaultdict(lambda: init_rating)
    for _, model_a, model_b, winner in df_battles[["model_a", "model_b", "winner"]].itertuples():
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
    battle_counts = df_battles["model_a"].value_counts() + df_battles["model_b"].value_counts()
    df_elos = df_elos.merge(battle_counts, left_on="model", right_index=True)
    df_bootstrap = get_bootstrap_result(df_battles, num_round=100)  # TODO: should precompute this
    df_elos = df_elos.merge(df_bootstrap.quantile(0.025).rename("q025"), left_on="model", right_index=True)
    df_elos = df_elos.merge(df_bootstrap.quantile(0.975).rename("q975"), left_on="model", right_index=True)
    # TODO: should we be doing this? fudge to ensure that elo isn't outside of CI
    df_elos["elo"] = df_elos.apply(lambda r: max(r.q025, min(r.elo, r.q975)), axis=1)
    df_elos["ci95"] = df_elos["q975"] - df_elos["q025"]
    return df_elos
