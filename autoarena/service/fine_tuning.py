from autoarena.api import api
from autoarena.service.task import TaskService


class FineTuningService:
    # TODO: this is just a placeholder for now
    @staticmethod
    def create_task(project_slug: str, request: api.CreateFineTuningTaskRequest) -> None:
        # 1. kick off fine-tuning job
        # 2. create judge when complete
        api_task = TaskService.create(project_slug, api.TaskType.FINE_TUNE)
        TaskService.Task(project_slug, api_task).update(f"Fine-tuning '{request.base_model}' base model", progress=0.1)
