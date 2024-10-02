import pandas as pd


def id_slug(a: int, b: int) -> str:
    return f"{int(min(a, b))}-{int(max(a, b))}"  # loaded as a sqlite extension


def invert_winner(winner: str) -> str:
    return "B" if winner == "A" else "A" if winner == "B" else winner


def check_required_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    missing_columns = set(required_columns) - set(df.columns)
    if len(missing_columns) > 0:
        raise ValueError(f"Missing {len(missing_columns)} required column(s): {missing_columns}")
