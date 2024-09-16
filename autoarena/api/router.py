from collections import OrderedDict
from io import BytesIO, StringIO
from typing import Optional

import pandas as pd
from fastapi import APIRouter, UploadFile, BackgroundTasks
from starlette.requests import Request
from starlette.responses import StreamingResponse

from autoarena.api import api
from autoarena.api.utils import SSEStreamingResponse
from autoarena.error import NotFoundError, BadRequestError
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
        request: Request,
        background_tasks: BackgroundTasks,
    ) -> list[api.Model]:
        # ideally there wouldn't be this much complexity in the router, but this is a complex form to parse
        form = await request.form()
        df_response_by_model_name: dict[str, pd.DataFrame] = OrderedDict()
        for key, value in form.items():
            model_name_slug = "||model_name"
            if not key.endswith(model_name_slug):
                continue
            file: UploadFile = form[key[: -len(model_name_slug)]]
            if file.content_type != "text/csv":
                raise ValueError(f"unsupported file type: {file.content_type}")
            df_response_by_model_name[value] = pd.read_csv(BytesIO(await file.read()))
        if len(df_response_by_model_name) == 0:
            raise BadRequestError("No valid model responses in body")
        new_models = [
            ModelService.upload_responses(project_slug, model_name, df_response)
            for model_name, df_response in df_response_by_model_name.items()
        ]
        background_tasks.add_task(TaskService.auto_judge, project_slug, models=new_models)
        return new_models

    @r.get("/project/{project_slug}/model/{model_id}/responses")
    def get_model_responses(project_slug: str, model_id: int) -> list[api.ModelResponse]:
        return ModelService.get_responses(project_slug, model_id)

    # TODO: potentially remove this -- it's not intuitive to have this trigger exist at the per-model level
    @r.post("/project/{project_slug}/model/{model_id}/judge")
    def trigger_model_auto_judge(project_slug: str, model_id: int, background_tasks: BackgroundTasks) -> None:
        model = ModelService.get_by_id(project_slug, model_id)
        background_tasks.add_task(TaskService.auto_judge, project_slug, models=[model])

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

    @r.get("/project/{project_slug}/head-to-head/count")
    def get_head_to_head_count(project_slug: str) -> int:
        return HeadToHeadService.get_count(project_slug)

    @r.post("/project/{project_slug}/head-to-head/vote")
    def submit_head_to_head_vote(
        project_slug: str,
        request: api.HeadToHeadVoteRequest,
        background_tasks: BackgroundTasks,
    ) -> None:
        HeadToHeadService.submit_vote(project_slug, request)
        # recompute confidence intervals in the background if we aren't doing so already
        background_tasks.add_task(TaskService.recompute_leaderboard, project_slug)

    @r.get("/project/{project_slug}/tasks")
    def get_tasks(project_slug: str) -> list[api.Task]:
        return TaskService.get_all(project_slug)

    @r.get("/project/{project_slug}/task/{task_id}/stream")
    async def get_task_stream(project_slug: str, task_id: int) -> StreamingResponse:  # Iterator[api.Task]
        return SSEStreamingResponse(TaskService.get_stream(project_slug, task_id))

    @r.get("/project/{project_slug}/tasks/has-active")
    async def get_has_active_tasks_stream(
        project_slug: str,
        timeout: Optional[float] = None,
    ) -> StreamingResponse:  # Iterator[api.HasActiveTasks]
        return SSEStreamingResponse(TaskService.has_active_stream(project_slug, timeout=timeout))

    @r.delete("/project/{project_slug}/tasks/completed")
    def delete_completed(project_slug: str) -> None:
        TaskService.delete_completed(project_slug)

    @r.post("/project/{project_slug}/task/auto-judge")
    def trigger_auto_judge(
        project_slug: str,
        request: api.TriggerAutoJudgeRequest,
        background_tasks: BackgroundTasks,
    ) -> None:
        judges = [j for j in JudgeService.get_all(project_slug) if j.id in set(request.judge_ids)]
        kwargs = dict(judges=judges, fraction=request.fraction, skip_existing=request.skip_existing)
        background_tasks.add_task(TaskService.auto_judge, project_slug, **kwargs)

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
