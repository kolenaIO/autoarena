from io import BytesIO, StringIO
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, UploadFile, Form, BackgroundTasks
from starlette.responses import StreamingResponse

from autoarena.api import api
from autoarena.service.elo import EloService
from autoarena.service.fine_tuning import FineTuningService
from autoarena.service.head_to_head import HeadToHeadService
from autoarena.service.project import ProjectService
from autoarena.service.judge import JudgeService
from autoarena.service.task import TaskService
from autoarena.service.model import ModelService


def router() -> APIRouter:
    r = APIRouter()

    @r.get("/projects")
    def get_projects() -> list[api.Project]:
        return ProjectService.get_all()

    @r.put("/project")
    def create_project(request: api.CreateProjectRequest) -> api.Project:
        return ProjectService.create_idempotent(request)

    @r.delete("/project/{project_id}")
    def delete_project(project_id: int) -> None:
        return ProjectService.delete(project_id)

    @r.get("/models/{project_id}")
    def get_models(project_id: int) -> list[api.Model]:
        return ModelService.get_all(project_id)

    @r.get("/models/{project_id}/by-judge/{judge_id}")
    def get_models_ranked_by_judge(project_id: int, judge_id: int) -> list[api.Model]:
        return ModelService.get_all_ranked_by_judge(project_id, judge_id)

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
    def get_elo_history(model_id: int, judge_id: int | None = None) -> list[api.EloHistoryItem]:
        return EloService.get_history(model_id, judge_id)

    @r.post("/model/{model_id}/judge")
    def trigger_model_judgement(model_id: int, background_tasks: BackgroundTasks) -> None:
        project_id = ModelService.get_project_id(model_id)
        model_name = ModelService.get_by_id(model_id).name
        background_tasks.add_task(TaskService.auto_judge, project_id, model_id, model_name)

    @r.delete("/model/{model_id}")
    def delete_model(model_id: int, background_tasks: BackgroundTasks) -> None:
        # TODO: this should technically be idempotent, but will currently fail if the model does not exist
        project_id = ModelService.get_project_id(model_id)
        ModelService.delete(model_id)
        background_tasks.add_task(TaskService.recompute_confidence_intervals, project_id)

    # async for StreamingResponses to improve speed; see https://github.com/fastapi/fastapi/issues/2302
    @r.get("/model/{model_id}/download/results")
    async def download_model_results_csv(model_id: int) -> StreamingResponse:
        df_result = ModelService.get_df_result(model_id)
        model_name = df_result.iloc[0].model
        stream = StringIO()
        df_result.to_csv(stream, index=False)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = f'attachment; filename="{model_name}.csv"'
        return response

    @r.get("/model/{model_id}/download/head-to-heads")
    async def download_model_head_to_heads_csv(model_id: int) -> StreamingResponse:
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
        background_tasks.add_task(TaskService.recompute_confidence_intervals, request.project_id)

    @r.get("/tasks/{project_id}")
    def get_tasks(project_id: int) -> list[api.Task]:
        return TaskService.get_all(project_id)

    @r.delete("/tasks/{project_id}/completed")
    def delete_completed(project_id: int) -> None:
        TaskService.delete_completed(project_id)

    @r.get("/judges/{project_id}")
    def get_judges(project_id: int) -> list[api.Judge]:
        return JudgeService.get_all(project_id)

    @r.get("/judge/default-system-prompt")
    def get_default_system_prompt() -> str:
        return JudgeService.get_default_system_prompt()

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

    @r.post("/fine-tune/{project_id}")
    def create_fine_tuning_task(project_id: int, request: api.CreateFineTuningTaskRequest) -> None:
        FineTuningService.create_task(project_id, request)

    return r
