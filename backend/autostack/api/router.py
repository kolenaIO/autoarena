from io import BytesIO, StringIO
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, UploadFile, Form, BackgroundTasks
from starlette.responses import StreamingResponse

from autostack.api import api
from autostack.service.elo import EloService
from autostack.service.head_to_head import HeadToHeadService
from autostack.service.project import ProjectService
from autostack.service.judge import JudgeService
from autostack.service.task import TaskService
from autostack.service.model import ModelService


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
        if file.content_type != "text/csv":
            raise ValueError(f"unsupported file type: {file.content_type}")
        df_result = pd.read_csv(BytesIO(contents))
        required_columns = {"prompt", "response"}
        missing_columns = required_columns - set(df_result.columns)
        if len(missing_columns) > 0:
            raise ValueError(f"missing required column(s): {missing_columns}")
        new_model = ModelService.upload_results(project_id, new_model_name, df_result)
        background_tasks.add_task(TaskService.auto_judge, project_id, new_model.id, new_model.name)
        return new_model

    @r.get("/model/{model_id}/results")
    def get_model_results(model_id: int) -> list[api.ModelResult]:
        return ModelService.get_results(model_id)

    @r.get("/model/{model_id}/elo-history")
    def get_elo_history(model_id: int) -> list[float]:
        return EloService.get_history(model_id)

    @r.delete("/model/{model_id}")
    def delete_model(model_id: int, background_tasks: BackgroundTasks) -> None:
        # TODO: this should technically be idempotent, but will currently fail if the model does not exist
        project_id = ModelService.get_project_id(model_id)
        ModelService.delete(model_id)
        background_tasks.add_task(TaskService.recompute_confidence_intervals, project_id)

    @r.get("/model/{model_id}/download/results")
    def download_model_results_csv(model_id: int) -> StreamingResponse:
        df_result = ModelService.get_df_result(model_id)
        model_name = df_result.iloc[0].model
        stream = StringIO()
        df_result.to_csv(stream, index=False)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = f'attachment; filename="{model_name}.csv"'
        return response

    @r.get("/model/{model_id}/download/head-to-heads")
    def download_model_head_to_heads_csv(model_id: int) -> StreamingResponse:
        df_result = ModelService.get_df_head_to_head(model_id)
        model = ModelService.get_by_id(model_id)
        stream = StringIO()
        df_result.to_csv(stream, index=False)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = f'attachment; filename="{model.name}-head-to-head.csv"'
        return response

    @r.get("/model/{model_id}/head-to-head/stats")
    def get_head_to_head_stats(model_id: int) -> list[api.ModelHeadToHeadStats]:
        return ModelService.get_head_to_head_stats(model_id)

    @r.put("/head-to-heads")
    def get_head_to_heads(request: api.HeadToHeadsRequest) -> list[api.HeadToHead]:
        return HeadToHeadService.get(request)

    @r.post("/head-to-head/judgement")
    def submit_head_to_head_judgement(
        request: api.HeadToHeadJudgementRequest, background_tasks: BackgroundTasks
    ) -> None:
        HeadToHeadService.submit_judgement(request)
        # recompute confidence intervals in the background if we aren't doing so already
        task_objects = TaskService.get_all(request.project_id)
        if len([t for t in task_objects if t.task_type == "recompute-confidence-intervals" and t.progress < 1]) == 0:
            background_tasks.add_task(TaskService.recompute_confidence_intervals, request.project_id)

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
    def delete_judge(judge_id: int, background_tasks: BackgroundTasks) -> None:
        # TODO: this should technically be idempotent, but will currently fail if the judge does not exist
        project_id = JudgeService.get_project_id(judge_id)
        JudgeService.delete(judge_id)
        background_tasks.add_task(TaskService.recompute_confidence_intervals, project_id)

    @r.put("/elo/reseed-scores/{project_id}")
    def reseed_scores(project_id: int) -> None:
        EloService.reseed_scores(project_id)

    return r
