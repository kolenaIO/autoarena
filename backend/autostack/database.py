from pathlib import Path

import pandas as pd

DATABASE_DIRECTORY = (Path(__file__).parent / ".." / ".data").resolve()
DATABASE_FILE = DATABASE_DIRECTORY / "models.parquet"

_DF: pd.DataFrame | None = None


def get_df_models() -> pd.DataFrame:
    global _DF
    if _DF is None:
        _DF = pd.read_parquet(DATABASE_FILE)
    return _DF


def setup_database() -> None:
    DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)
