from autoarena.api import api
from autoarena.service.task import TaskService


class FineTuningService:
    # TODO: this is just a placeholder for now
    @staticmethod
    def create_task(project_id: int, request: api.CreateFineTuningTaskRequest) -> None:
        # 1. kick off fine-tuning job
        # 2. create judge when complete
        task_id = TaskService.create(project_id, "fine-tune").id
        TaskService.update(task_id, status=f"Fine-tuning '{request.base_model}' base model", progress=0.1)
