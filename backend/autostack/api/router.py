from dataclasses import dataclass

from fastapi import APIRouter

from autostack.api.service import compute_all_model_elos, Model
from autostack.store.database import get_df_battle


@dataclass(frozen=True)
class BattlesRequest:
    project_id: int
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

    @r.get("/models/{project_id}")
    def get_models(project_id: int) -> list[Model]:
        return compute_all_model_elos(project_id)

    @r.put("/battles")
    def get_battles(request: BattlesRequest) -> list[Battle]:
        df_battles = get_df_battle(request.project_id)
        df_battles = df_battles[df_battles["model_a_id"].isin({request.model_a_id, request.model_b_id})]
        df_battles = df_battles[df_battles["model_b_id"].isin({request.model_a_id, request.model_b_id})]
        for condition in [
            df_battles["model_b_id"] == request.model_a_id,
            df_battles["model_a_id"] == request.model_b_id,
        ]:
            cols = ["response_a", "response_b"]
            df_battles.loc[condition, cols] = df_battles.loc[condition, cols[::-1]].values
        return [
            Battle(id=r.battle_id, prompt=r.prompt, response_a=r.response_a, response_b=r.response_b)
            for r in df_battles.itertuples()
        ]

    return r
