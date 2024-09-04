import pandas as pd

from autostack.service.elo import EloService


# TODO: this is a placeholder
def test__compute_elo() -> None:
    df_h2h = pd.DataFrame([], columns=["model_a", "model_b", "winner"])
    df_elo = EloService.compute_elo(df_h2h)
    assert len(df_elo) == 0
