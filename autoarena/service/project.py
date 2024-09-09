from contextlib import contextmanager
from pathlib import Path

import duckdb
from loguru import logger

from autoarena.api import api
from autoarena.error import NotFoundError
from autoarena.judge.human import HumanJudge
from autoarena.store import database
from autoarena.store.database import get_database_connection, SCHEMA_FILE


class ProjectService:
    @staticmethod
    @contextmanager
    def connect(slug: str) -> duckdb.DuckDBPyConnection:
        path = ProjectService._slug_to_path(slug)
        if not path.exists():
            raise NotFoundError(f"File for project '{slug}' not found (expected: {path})")
        with get_database_connection(path) as conn:
            yield conn

    @staticmethod
    def get_all() -> list[api.Project]:
        paths = sorted(list(database.get_data_directory().glob("*.duckdb")))
        return [api.Project(slug=ProjectService._path_to_slug(p), filename=p.name, filepath=str(p)) for p in paths]

    @staticmethod
    def create_idempotent(request: api.CreateProjectRequest) -> api.Project:
        # TODO: should come up with a better way than this to have services point at one another, or remove the need
        from autoarena.service.judge import JudgeService

        data_directory = database.get_data_directory()
        data_directory.mkdir(parents=True, exist_ok=True)
        path = data_directory / f"{request.name}.duckdb"
        slug = ProjectService._path_to_slug(path)
        ProjectService._setup_database(path)
        JudgeService.create_idempotent(slug, HumanJudge())
        return api.Project(slug=slug, filename=path.name, filepath=str(path))

    @staticmethod
    def delete(slug: str) -> None:
        path = ProjectService._slug_to_path(slug)
        path.unlink(missing_ok=True)
        logger.info(f"Removed file '{path}' containing project '{slug}'")

    @staticmethod
    def _path_to_slug(path: Path) -> str:
        return path.stem

    @staticmethod
    def _slug_to_path(slug: str) -> Path:
        return database.get_data_directory() / f"{slug}.duckdb"

    @staticmethod
    def _setup_database(path: Path) -> None:
        schema_sql = SCHEMA_FILE.read_text()
        with get_database_connection(path) as conn:
            conn.sql(schema_sql)
        ProjectService._close_pending_tasks()

    # TODO: restart pending tasks rather than simply terminating
    @staticmethod
    def _close_pending_tasks() -> None:
        from autoarena.service.task import TaskService

        projects = ProjectService.get_all()
        for project in projects:
            tasks = TaskService.get_all(project.slug)
            for task in tasks:
                if task.progress < 1:
                    TaskService.update(project.slug, task.id, status="Terminated", progress=1)
