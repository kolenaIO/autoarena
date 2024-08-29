from dataclasses import dataclass
from datetime import datetime

from fastapi import APIRouter

from autostack.database import get_df_models
from autostack.database import get_df_battles


@dataclass(frozen=True)
class Model:
    id: int
    name: str
    created: datetime
    elo: float
    q025: float
    q975: float
    votes: int


@dataclass(frozen=True)
class BattlesRequest:
    model_a_id: int
    model_b_id: int


@dataclass(frozen=True)
class Battle:
    id: int
    prompt: str
    response_a: str
    response_b: str


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

    @r.put("/battles")
    def get_battles(request: BattlesRequest) -> list[Battle]:
        df_battles = get_df_battles()
        df_models = get_df_models()
        # TODO: dirty
        model_a_name = df_models.loc[df_models["rank_true"] == request.model_a_id].iloc[0].model
        model_b_name = df_models.loc[df_models["rank_true"] == request.model_b_id].iloc[0].model
        df_battles = df_battles[df_battles["model_a"].isin({model_a_name, model_b_name})]
        df_battles = df_battles[df_battles["model_b"].isin({model_a_name, model_b_name})]
        for condition in [df_battles["model_b"] == model_a_name, df_battles["model_a"] == model_b_name]:
            df_battles.loc[condition, ["model_a", "model_b"]] = df_battles.loc[condition, ["model_b", "model_a"]].values
        return [
            Battle(id=r.id, prompt=r.prompt, response_a=r.response_a, response_b=r.response_b)
            for r in df_battles.itertuples()
        ]

    return r
