import argparse
from pathlib import Path

import pandas as pd

from autoarena.api import api
from autoarena.judge.human import HumanJudge
from autoarena.service.elo import EloService
from autoarena.service.head_to_head import HeadToHeadService
from autoarena.service.judge import JudgeService
from autoarena.service.model import ModelService
from autoarena.service.project import ProjectService


def seed_head_to_heads(head_to_heads: Path) -> None:
    df = pd.read_parquet(head_to_heads) if head_to_heads.suffix == ".parquet" else pd.read_csv(head_to_heads)

    # 1. seed project
    project_slug = ProjectService.create_idempotent(api.CreateProjectRequest(name=head_to_heads.stem)).slug

    # 2. seed models
    models = set(df.model_a) & set(df.model_b)
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
    df["judge_id"] = [j for j in JudgeService.get_all(project_slug) if j.name == HumanJudge().name][0].id
    HeadToHeadService.upload_head_to_heads(project_slug, df[["response_a_id", "response_b_id", "judge_id", "winner"]])

    # 4. seed elo scores
    EloService.reseed_scores(project_slug)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
Seed a new project from a CSV or Parquet file where each row represents a head-to-head matchup between two models.

The following columns are required:

- `model_a`: name of model A in this head-to-head
- `model_b`: name of model B in this head-to-head
- `prompt`: the prompt that both models were run on
- `response_a`: the response from model A to the prompt
- `response_b`: the response from model B to the prompt
- `winner`: the winner of the head-to-head, either "A", "B", or "-" for ties""",
    )
    ap.add_argument("head_to_heads", type=Path, help="Path to .csv or .parquet file with head-to-heads and judgements")
    args = ap.parse_args()
    seed_head_to_heads(args.head_to_heads)
