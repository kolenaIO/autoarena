from pathlib import Path

import pandas as pd

from autoarena.api import api
from autoarena.service.model import ModelService
from autoarena.service.project import ProjectService
from autoarena.service.judge import JudgeService
from autoarena.service.task import TaskService
from autoarena.service.elo import EloService
from autoarena.judge.human import HumanJudge
from autoarena.store.database import SCHEMA_FILE, get_database_connection


def setup_database() -> None:
    schema_sql = SCHEMA_FILE.read_text()
    with get_database_connection() as conn:
        conn.sql(schema_sql)
    close_pending_tasks()


# TODO: this should call an API rather than hand-rolling here -- at the very least use services to manipulate database
def seed_initial_battles(battles_parquet: str) -> None:
    project_name = Path(battles_parquet).stem
    df_battles = pd.read_parquet(battles_parquet)

    # 2. seed with project
    project_id = ProjectService.create_idempotent(api.CreateProjectRequest(name=project_name)).id
    human_judge = HumanJudge()
    judge_id = [j for j in JudgeService.get_all(project_id) if j.name == human_judge.name][0].id

    # 3. seed with models
    with get_database_connection() as conn:
        models = list(set(df_battles["model_a"]) & set(df_battles["model_b"]))
        df_model = pd.DataFrame([(project_id, m) for m in models], columns=["project_id", "name"])
        conn.sql("""
            INSERT INTO model (project_id, name)
            SELECT project_id, name
            FROM df_model
            ON CONFLICT (project_id, name) DO NOTHING
        """)

    # 4. seed with results
    df_model = ModelService.get_all_df(project_id)
    result_cols_a = ["model_a", "prompt", "response_a"]
    df_result_a = df_battles[result_cols_a].rename(columns=dict(model_a="model", response_a="response"))
    result_cols_b = ["model_b", "prompt", "response_b"]
    df_result_b = df_battles[result_cols_b].rename(columns=dict(model_b="model", response_b="response"))
    df_result = pd.concat([df_result_a, df_result_b])
    df_result = pd.merge(df_result, df_model, left_on="model", right_on="name", how="left")
    df_result = df_result[df_result["response"].notna()]  # drop empty responses
    df_result = df_result.drop_duplicates(subset=["id", "prompt"], keep="last")  # drop duplicate rows
    with get_database_connection() as conn:
        conn.sql("""
            INSERT INTO result (model_id, prompt, response)
            SELECT id, prompt, response
            FROM df_result
            ON CONFLICT (model_id, prompt) DO NOTHING
        """)
        df_result = conn.execute(
            """
            SELECT r.id AS result_a_id, m.name AS model, prompt, response
            FROM result r
            JOIN model m ON m.id = r.model_id
            WHERE m.project_id = $project_id
        """,
            dict(project_id=project_id),
        ).df()

    # 5. seed with battles
    right_on = ["model", "prompt"]
    df_battle = pd.merge(df_battles, df_result, left_on=["model_a", "prompt"], right_on=right_on, how="left")
    df_result = df_result.rename(columns=dict(result_a_id="result_b_id"))
    df_battle = pd.merge(df_battle, df_result, left_on=["model_b", "prompt"], right_on=right_on, how="left")
    df_battle = df_battle[df_battle["result_a_id"].notna()]  # drop empty battles
    df_battle = df_battle[df_battle["result_b_id"].notna()]  # drop empty battles
    df_battle["result_id_slug"] = df_battle.apply(
        lambda r: f"{int(min(r.result_a_id, r.result_b_id))}-{int(max(r.result_a_id, r.result_b_id))}", axis=1
    )
    df_battle = df_battle.drop_duplicates(subset=["result_id_slug"], keep="last")
    df_battle["judge_id"] = judge_id
    with get_database_connection() as conn:
        conn.execute("""
            INSERT INTO battle (result_id_slug, result_a_id, result_b_id, judge_id, winner)
            SELECT id_slug(result_a_id, result_b_id), result_a_id, result_b_id, judge_id, winner
            FROM df_battle
            ON CONFLICT (result_id_slug, judge_id) DO NOTHING
        """)

    # 6. seed with elo scores (when necessary)
    if (df_model["elo"] == 1000).all():
        EloService.reseed_scores(project_id)


# TODO: restart pending tasks rather than simply terminating
def close_pending_tasks() -> None:
    projects = ProjectService.get_all()
    for project in projects:
        tasks = TaskService.get_all(project.id)
        for task in tasks:
            if task.progress < 1:
                TaskService.update(task.id, status="Terminated", progress=1)
