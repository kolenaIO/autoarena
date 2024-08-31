import dataclasses
from io import BytesIO
from random import randint
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, UploadFile, Form, BackgroundTasks

from autostack.api import api
from autostack.api.service import ProjectService, JudgeService, TaskService, ModelService
from autostack.elo import compute_elo_single
from autostack.judge.human import HumanJudge
from autostack.tasks import recompute_confidence_intervals, auto_judge
from autostack.store.database import get_database_connection


def router() -> APIRouter:
    r = APIRouter()

    @r.get("/projects")
    def get_projects() -> list[api.Project]:
        return ProjectService.get_all()

    @r.put("/project")
    def create_project(request: api.CreateProjectRequest) -> api.Project:
        return ProjectService.create_idempotent(request)

    @r.get("/models/{project_id}")
    def get_models(project_id: int) -> list[api.Model]:
        return ModelService.get_all(project_id)

    @r.post("/model")
    async def upload_model_results(
        file: UploadFile,
        new_model_name: Annotated[str, Form()],
        project_id: Annotated[int, Form()],
        background_tasks: BackgroundTasks,
    ) -> api.Model:
        contents = await file.read()
        if file.content_type == "text/csv":
            df = pd.read_csv(BytesIO(contents))
        else:
            raise ValueError(f"unsupported file type: {file.content_type}")

        required_columns = {"prompt", "response"}
        missing_columns = required_columns - set(df.columns)
        if len(missing_columns) > 0:
            raise ValueError(f"missing required column(s): {missing_columns}")

        with get_database_connection() as conn:
            params = dict(project_id=project_id, model_name=new_model_name)
            ((new_model_id,),) = conn.execute(
                """
                INSERT INTO model (project_id, name)
                VALUES ($project_id, $model_name)
                RETURNING id
                """,
                params,
            ).fetchall()
            df["model_id"] = new_model_id
            conn.execute("""
                INSERT INTO result (model_id, prompt, response)
                SELECT model_id, prompt, response
                FROM df
            """)

        models = ModelService.get_all(project_id)
        new_model = [model for model in models if model.id == new_model_id][0]
        background_tasks.add_task(auto_judge, project_id, new_model_id, new_model.name)
        return new_model

    @r.put("/head-to-heads")
    def get_head_to_heads(request: api.HeadToHeadsRequest) -> list[api.HeadToHead]:
        with get_database_connection() as conn:
            df_h2h = conn.execute(
                """
                SELECT
                    ra.id AS result_a_id,
                    rb.id AS result_b_id,
                    ra.prompt AS prompt,
                    ra.response AS response_a,
                    rb.response AS response_b
                FROM result ra
                JOIN result rb ON ra.prompt = rb.prompt
                WHERE ra.model_id = $model_a_id
                AND rb.model_id = $model_b_id
            """,
                dict(model_a_id=request.model_a_id, model_b_id=request.model_b_id),
            ).df()
        return [api.HeadToHead(**r) for _, r in df_h2h.iterrows()]

    @r.post("/head-to-head/judgement")
    def submit_head_to_head_judgement(
        request: api.HeadToHeadJudgementRequest, background_tasks: BackgroundTasks
    ) -> None:
        with get_database_connection() as conn:
            # 1. create human judge if necessary
            human_judge = HumanJudge()
            JudgeService.create_idempotent(request.project_id, human_judge)

            # 2. insert battle record
            conn.execute(
                """
                INSERT INTO battle (result_a_id, result_b_id, judge_id, winner)
                SELECT $result_a_id, $result_b_id, j.id, $winner
                FROM judge j
                WHERE j.project_id = $project_id
                AND j.name = $judge_name
                ON CONFLICT (result_a_id, result_b_id, judge_id) DO UPDATE SET winner = EXCLUDED.winner
            """,
                dict(**dataclasses.asdict(request), judge_name=human_judge.name),
            )

            # 3. adjust elo scores
            df_model = conn.execute(
                """
                SELECT id, elo
                FROM model m
                WHERE EXISTS (SELECT 1 FROM result r WHERE r.id = $result_a_id AND r.model_id = m.id)
                UNION ALL
                SELECT id, elo
                FROM model m
                WHERE EXISTS (SELECT 1 FROM result r WHERE r.id = $result_b_id AND r.model_id = m.id)
            """,
                dict(result_a_id=request.result_a_id, result_b_id=request.result_b_id),
            ).df()
            model_a = df_model.iloc[0]
            model_b = df_model.iloc[1]
            elo_a, elo_b = compute_elo_single(model_a.elo, model_b.elo, request.winner)
            for model_id, elo in [(model_a.id, elo_a), (model_b.id, elo_b)]:
                conn.execute("UPDATE model SET elo = $elo WHERE id = $model_id", dict(model_id=model_id, elo=elo))

        # TODO: this is a dirty hack but it's too expensive to run this on every vote
        # 4. recompute confidence intervals in the background
        if randint(0, 10) == 0:
            background_tasks.add_task(recompute_confidence_intervals, request.project_id)

    @r.get("/tasks/{project_id}")
    def get_tasks(project_id: int) -> list[api.Task]:
        return TaskService.get_all(project_id)

    @r.get("/judges/{project_id}")
    def get_judges(project_id: int) -> list[api.Judge]:
        return JudgeService.get_all(project_id)

    @r.post("/judge")
    def create_judge(request: api.CreateJudgeRequest) -> api.Judge:
        return JudgeService.create(request)

    @r.put("/judge")
    def update_judge(request: api.UpdateJudgeRequest) -> api.Judge:
        return JudgeService.update(request)

    @r.delete("/judge/{judge_id}")
    def delete_judge(judge_id: int) -> None:
        return JudgeService.delete(judge_id)

    return r
