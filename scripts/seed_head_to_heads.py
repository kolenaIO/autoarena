import argparse
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from autoarena.api import api
from autoarena.judge.human import HumanJudge
from autoarena.service.elo import EloService
from autoarena.service.head_to_head import HeadToHeadService
from autoarena.service.judge import JudgeService
from autoarena.service.model import ModelService
from autoarena.service.project import ProjectService
from autoarena.store.seed import setup_database


def seed_head_to_heads(head_to_heads: str) -> None:
    project_name = Path(head_to_heads).stem
    df = pd.read_parquet(head_to_heads)

    # 1. seed project
    setup_database()
    project_id = ProjectService.create_idempotent(api.CreateProjectRequest(name=project_name)).id

    # 2. seed models
    models = set(df.model_a) & set(df.model_b)
    model_ids: list[int] = []
    for model in tqdm(models, total=len(models), desc="seed models"):
        cols = ["prompt", "response"]
        df_model_result_a = df[df.model_a == model].rename(columns=dict(response_a="response"))[cols]
        df_model_result_b = df[df.model_b == model].rename(columns=dict(response_b="response"))[cols]
        df_model_result = pd.concat([df_model_result_a, df_model_result_b])
        df_model_result = df_model_result.drop_duplicates(subset=["prompt"], keep="last")  # drop duplicate rows
        df_model_result = df_model_result.dropna(subset=["response"])
        model_ids.append(ModelService.upload_results(project_id, model, df_model_result).id)

    # 3. seed head-to-heads
    df_result = pd.concat([ModelService.get_df_result(model_id) for model_id in model_ids])
    right_on = ["model", "prompt", "response"]
    df = df.merge(df_result, left_on=["model_a", "prompt", "response_a"], right_on=right_on, how="left")
    df = df.rename(columns=dict(result_id="result_a_id"))
    df = df.merge(df_result, left_on=["model_b", "prompt", "response_b"], right_on=right_on, how="left")
    df = df.rename(columns=dict(result_id="result_b_id"))
    df = df.dropna(subset=["result_a_id", "result_b_id"])
    df[["result_a_id", "result_b_id"]] = df[["result_a_id", "result_b_id"]].astype(int)
    df["judge_id"] = [j for j in JudgeService.get_all(project_id) if j.name == HumanJudge().name][0].id
    HeadToHeadService.upload_head_to_heads(df[["result_a_id", "result_b_id", "judge_id", "winner"]])

    # 4. seed elo scores
    EloService.reseed_scores(project_id)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("head_to_heads", help="Path to parquet file with head-to-heads and judgements")
    args = ap.parse_args()
    seed_head_to_heads(args.head_to_heads)
