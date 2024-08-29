from dataclasses import dataclass
from datetime import datetime

from fastapi import APIRouter

from autostack.database import get_df_models


@dataclass(frozen=True)
class Model:
    id: int
    name: str
    created: datetime
    elo: float
    q025: float
    q975: float
    votes: int


def router() -> APIRouter:
    r = APIRouter()

    @r.get("/models")
    def get_models() -> list[Model]:
        df_models = get_df_models()
        return [
            Model(
                id=r.rank_true,
                name=r.model,
                created=datetime.utcnow(),  # r.created, TODO
                elo=r.elo_true,
                q025=r.q025_true,
                q975=r.q975_true,
                votes=r.count_true,
            )
            for r in df_models.itertuples()
        ]

    return r
