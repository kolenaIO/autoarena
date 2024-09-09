from io import BytesIO, StringIO
from typing import Annotated, Optional

import pandas as pd
from fastapi import APIRouter, UploadFile, Form, BackgroundTasks
from starlette.responses import StreamingResponse

from autoarena.api import api
from autoarena.error import NotFoundError
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

    @r.delete("/project/{project_slug}")
    def delete_project(project_slug: str) -> None:
        return ProjectService.delete(project_slug)

    @r.get("/project/{project_slug}/models")
    def get_models(project_slug: str) -> list[api.Model]:
        return ModelService.get_all(project_slug)

    @r.get("/project/{project_slug}/models/by-judge/{judge_id}")
    def get_models_ranked_by_judge(project_slug: str, judge_id: int) -> list[api.Model]:
        return ModelService.get_all_ranked_by_judge(project_slug, judge_id)

    @r.post("/project/{project_slug}/model")
    async def upload_model_responses(
        project_slug: str,
        file: UploadFile,
        new_model_name: Annotated[str, Form()],
        background_tasks: BackgroundTasks,
    ) -> api.Model:
        if file.content_type != "text/csv":
            raise ValueError(f"unsupported file type: {file.content_type}")
        df_response = pd.read_csv(BytesIO(await file.read()))
        new_model = ModelService.upload_responses(project_slug, new_model_name, df_response)
        background_tasks.add_task(TaskService.auto_judge, project_slug, new_model.id, new_model.name)
        return new_model

    @r.get("/project/{project_slug}/model/{model_id}/responses")
    def get_model_responses(project_slug: str, model_id: int) -> list[api.ModelResponse]:
        return ModelService.get_responses(project_slug, model_id)

    @r.get("/project/{project_slug}/model/{model_id}/elo-history")
    def get_elo_history(project_slug: str, model_id: int, judge_id: Optional[int] = None) -> list[api.EloHistoryItem]:
        return EloService.get_history(project_slug, model_id, judge_id)

    @r.post("/project/{project_slug}/model/{model_id}/judge")
    def trigger_model_judgement(project_slug: str, model_id: int, background_tasks: BackgroundTasks) -> None:
        model_name = ModelService.get_by_id(project_slug, model_id).name
        background_tasks.add_task(TaskService.auto_judge, project_slug, model_id, model_name)

    @r.delete("/project/{project_slug}/model/{model_id}")
    def delete_model(project_slug: str, model_id: int, background_tasks: BackgroundTasks) -> None:
        try:
            ModelService.delete(project_slug, model_id)
            background_tasks.add_task(TaskService.recompute_leaderboard, project_slug)
        except NotFoundError:
            pass

    # async for StreamingResponses to improve speed; see https://github.com/fastapi/fastapi/issues/2302
    @r.get("/project/{project_slug}/model/{model_id}/download/responses")
    async def download_model_responses_csv(project_slug: str, model_id: int) -> StreamingResponse:
        columns = ["prompt", "response"]
        df_response = ModelService.get_df_response(project_slug, model_id)
        model_name = df_response.iloc[0].model
        stream = StringIO()
        df_response[columns].to_csv(stream, index=False)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = f'attachment; filename="{model_name}.csv"'
        return response

    @r.get("/project/{project_slug}/model/{model_id}/download/head-to-heads")
    async def download_model_head_to_heads_csv(project_slug: str, model_id: int) -> StreamingResponse:
        columns = ["prompt", "model_a", "model_b", "response_a", "response_b", "judge", "winner"]
        df_h2h = ModelService.get_df_head_to_head(project_slug, model_id)
        model = ModelService.get_by_id(project_slug, model_id)
        stream = StringIO()
        df_h2h[columns].to_csv(stream, index=False)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = f'attachment; filename="{model.name}-head-to-head.csv"'
        return response

    @r.get("/project/{project_slug}/model/{model_id}/head-to-head/stats")
    def get_head_to_head_stats(project_slug: str, model_id: int) -> list[api.ModelHeadToHeadStats]:
        return ModelService.get_head_to_head_stats(project_slug, model_id)

    @r.put("/project/{project_slug}/head-to-heads")
    def get_head_to_heads(project_slug: str, request: api.HeadToHeadsRequest) -> list[api.HeadToHead]:
        return HeadToHeadService.get(project_slug, request)

    @r.post("/project/{project_slug}/head-to-head/judgement")
    def submit_head_to_head_judgement(
        project_slug: str,
        request: api.HeadToHeadJudgementRequest,
        background_tasks: BackgroundTasks,
    ) -> None:
        HeadToHeadService.submit_judgement(project_slug, request)
        # recompute confidence intervals in the background if we aren't doing so already
        background_tasks.add_task(TaskService.recompute_leaderboard, project_slug)

    @r.get("/project/{project_slug}/tasks")
    def get_tasks(project_slug: str) -> list[api.Task]:
        return TaskService.get_all(project_slug)

    @r.delete("/project/{project_slug}/tasks/completed")
    def delete_completed(project_slug: str) -> None:
        TaskService.delete_completed(project_slug)

    @r.get("/project/{project_slug}/judges")
    def get_judges(project_slug: str) -> list[api.Judge]:
        return JudgeService.get_all(project_slug)

    @r.get("/project/{project_slug}/judge/default-system-prompt")
    def get_default_system_prompt(project_slug: str) -> str:
        return JudgeService.get_default_system_prompt()

    @r.post("/project/{project_slug}/judge")
    def create_judge(project_slug: str, request: api.CreateJudgeRequest) -> api.Judge:
        return JudgeService.create(project_slug, request)

    @r.put("/project/{project_slug}/judge/{judge_id}")
    def update_judge(project_slug: str, judge_id: int, request: api.UpdateJudgeRequest) -> api.Judge:
        return JudgeService.update(project_slug, judge_id, request)

    @r.get("/project/{project_slug}/judge/{judge_type}/can-access")
    def check_can_access(project_slug: str, judge_type: api.JudgeType) -> bool:
        return JudgeService.check_can_access(judge_type)

    @r.delete("/project/{project_slug}/judge/{judge_id}")
    def delete_judge(project_slug: str, judge_id: int, background_tasks: BackgroundTasks) -> None:
        try:
            JudgeService.delete(project_slug, judge_id)
            background_tasks.add_task(TaskService.recompute_leaderboard, project_slug)
        except NotFoundError:
            pass

    @r.put("/project/{project_slug}/elo/reseed-scores")
    def reseed_scores(project_slug: str) -> None:
        EloService.reseed_scores(project_slug)

    @r.post("/project/{project_slug}/fine-tune")
    def create_fine_tuning_task(project_slug: str, request: api.CreateFineTuningTaskRequest) -> None:
        FineTuningService.create_task(project_slug, request)

    return r
