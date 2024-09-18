from pathlib import Path

import pandas as pd

from autoarena.api import api
from autoarena.service.elo import EloService
from autoarena.service.head_to_head import HeadToHeadService
from autoarena.service.judge import JudgeService
from autoarena.service.model import ModelService
from autoarena.service.project import ProjectService
from autoarena.store.utils import check_required_columns


def seed_head_to_heads(head_to_heads: Path) -> None:
    df = pd.read_parquet(head_to_heads) if head_to_heads.suffix == ".parquet" else pd.read_csv(head_to_heads)
    check_required_columns(df, ["model_a", "model_b", "prompt", "response_a", "response_b", "winner"])

    # 1. seed project
    project_slug = ProjectService.create_idempotent(api.CreateProjectRequest(name=head_to_heads.stem)).slug

    # 2. seed models
    models = set(df.model_a) | set(df.model_b)
    model_ids: list[int] = []
    for model in models:
        cols = ["prompt", "response"]
        df_model_response_a = df[df.model_a == model].rename(columns=dict(response_a="response"))[cols]
        df_model_response_b = df[df.model_b == model].rename(columns=dict(response_b="response"))[cols]
        df_model_response = pd.concat([df_model_response_a, df_model_response_b])
        df_model_response = df_model_response.drop_duplicates(subset=["prompt"], keep="last")  # drop duplicate rows
        df_model_response = df_model_response.dropna(subset=["response"])
        model_ids.append(ModelService.upload_responses(project_slug, model, df_model_response).id)

    # 3. seed head-to-heads
    df_response = pd.concat([ModelService.get_df_response(project_slug, model_id) for model_id in model_ids])
    right_on = ["model", "prompt", "response"]
    df = df.merge(df_response, left_on=["model_a", "prompt", "response_a"], right_on=right_on, how="left")
    df = df.rename(columns=dict(response_id="response_a_id"))
    df = df.merge(df_response, left_on=["model_b", "prompt", "response_b"], right_on=right_on, how="left")
    df = df.rename(columns=dict(response_id="response_b_id"))
    df = df.dropna(subset=["response_a_id", "response_b_id"])
    df[["response_a_id", "response_b_id"]] = df[["response_a_id", "response_b_id"]].astype(int)
    # TODO: allow seeding with non-human judgements?
    df["judge_id"] = [j for j in JudgeService.get_all(project_slug) if j.judge_type is api.JudgeType.HUMAN][0].id
    HeadToHeadService.upload_head_to_heads(project_slug, df[["response_a_id", "response_b_id", "judge_id", "winner"]])

    # 4. seed elo scores
    EloService.reseed_scores(project_slug)
