from autoarena.service.project import ProjectService
from autoarena.service.task import TaskService
from autoarena.store.database import SCHEMA_FILE, get_database_connection


def setup_database() -> None:
    schema_sql = SCHEMA_FILE.read_text()
    with get_database_connection() as conn:
        conn.sql(schema_sql)
    close_pending_tasks()


# TODO: restart pending tasks rather than simply terminating
def close_pending_tasks() -> None:
    projects = ProjectService.get_all()
    for project in projects:
        tasks = TaskService.get_all(project.id)
        for task in tasks:
            if task.progress < 1:
                TaskService.update(task.id, status="Terminated", progress=1)
