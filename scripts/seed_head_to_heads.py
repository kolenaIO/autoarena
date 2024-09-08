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
from autoarena.store.utils import id_slug, setup_database


# TODO: this should call an API rather than hand-rolling here -- at the very least use services to manipulate database
def seed_head_to_heads(head_to_heads: str) -> None:
    project_name = Path(head_to_heads).stem
    df = pd.read_parquet(head_to_heads)

    # 1. seed with project
    setup_database()
    project_id = ProjectService.create_idempotent(api.CreateProjectRequest(name=project_name)).id

    # 2. seed with models
    models = set(df.model_a) & set(df.model_b)
    for model in tqdm(models, total=len(models), desc="seed models"):
        cols = ["prompt", "response"]
        df_model_result_a = df[df.model_a == model].rename(columns=dict(response_a="response"))[cols]
        df_model_result_b = df[df.model_b == model].rename(columns=dict(response_b="response"))[cols]
        df_model_result = pd.concat([df_model_result_a, df_model_result_b])
        df_model_result = df_model_result.drop_duplicates(subset=["prompt"], keep="last")  # drop duplicate rows
        df_model_result = df_model_result.dropna(subset=["response"])
        ModelService.upload_results(project_id, model, df_model_result)

    # 3. seed with head-to-heads
    df_model = ModelService.get_all_df(project_id)[["id", "name"]]
    df_results = []
    for r in tqdm(df_model.itertuples(), total=len(df_model), desc="load head-to-heads"):
        df_result = ModelService.get_df_result(r.id)
        df_result["name"] = r.name
        df_results.append(df_result)

    df_result = pd.concat(df_results)
    right_on = ["name", "prompt", "response"]
    df = df.merge(df_result, left_on=["model_a", "prompt", "response_a"], right_on=right_on, how="left")
    df = df.rename(columns=dict(result_id="result_a_id"))
    df = df.merge(df_result, left_on=["model_b", "prompt", "response_b"], right_on=right_on, how="left")
    df = df.rename(columns=dict(result_id="result_b_id"))
    df = df.dropna(subset=["result_a_id", "result_b_id"])
    df[["result_a_id", "result_b_id"]] = df[["result_a_id", "result_b_id"]].astype(int)
    df["result_id_slug"] = df.apply(lambda r: id_slug(r.result_a_id, r.result_b_id), axis=1)
    df = df.drop_duplicates(subset=["result_id_slug"], keep="first")
    df["judge_id"] = [j for j in JudgeService.get_all(project_id) if j.name == HumanJudge().name][0].id
    HeadToHeadService.upload_head_to_heads(df[["result_a_id", "result_b_id", "judge_id", "winner"]])

    # 4. seed with elo scores
    EloService.reseed_scores(project_id)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("head_to_heads", help="Path to parquet file with head-to-heads and judgements")
    args = ap.parse_args()
    seed_head_to_heads(args.head_to_heads)
