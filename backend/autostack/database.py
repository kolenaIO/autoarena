from pathlib import Path

import pandas as pd

DATABASE_DIRECTORY = (Path(__file__).parent / ".." / ".data").resolve()
DF_MODELS_FILE = DATABASE_DIRECTORY / "models.parquet"
DF_BATTLES_FILE = DATABASE_DIRECTORY / "battles.parquet"

_DF_MODELS: pd.DataFrame | None = None
_DF_BATTLES: pd.DataFrame | None = None


def setup_database() -> None:
    DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)


def get_df_models() -> pd.DataFrame:
    global _DF_MODELS
    if _DF_MODELS is None:
        _DF_MODELS = pd.read_parquet(DF_MODELS_FILE)
    return _DF_MODELS


def get_df_battles() -> pd.DataFrame:
    global _DF_BATTLES
    if _DF_BATTLES is None:
        _DF_BATTLES = pd.read_parquet(DF_BATTLES_FILE)
    return _DF_BATTLES
