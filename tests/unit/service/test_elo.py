import pandas as pd

from autoarena.service.elo import EloService, DEFAULT_ELO_CONFIG

DF_H2H = pd.DataFrame(
    [("a", "b", "A"), ("b", "a", "B"), ("a", "c", "-"), ("b", "c", "-")],
    columns=["model_a", "model_b", "winner"],
)


def test__elo_service__compute_elo() -> None:
    n_models = len(set(DF_H2H["model_a"]).union(set(DF_H2H["model_b"])))
    df_elo = EloService.compute_elo(DF_H2H)
    assert len(df_elo) == n_models
    assert df_elo.iloc[0].model == "a"
    assert df_elo.iloc[1].model == "c"
    assert df_elo.iloc[2].model == "b"
    assert all(df_elo.iloc[i - 1].elo > df_elo.iloc[i].elo for i in range(1, len(df_elo)))  # sorted by desc elo


def test__elo_service__compute_confidence_intervals() -> None:
    df_elo = EloService.compute_elo(DF_H2H)
    df_elo_ci = EloService.compute_confidence_intervals(df_elo, DF_H2H)
    assert all(df_elo_ci.elo == df_elo.elo)
    assert all(df_elo_ci["q025"].notna())
    assert all(df_elo_ci["q975"].notna())
    assert df_elo_ci.iloc[0].q025 >= DEFAULT_ELO_CONFIG.default_score  # can't be lower, didn't lose any
    assert df_elo_ci.iloc[-1].q975 <= DEFAULT_ELO_CONFIG.default_score  # can't be higher, didn't win any
