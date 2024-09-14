from contextlib import contextmanager
from pathlib import Path

import duckdb
from loguru import logger

from autoarena.api import api
from autoarena.error import NotFoundError, MigrationError
from autoarena.store.database import get_database_connection, get_data_directory, get_available_migrations


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
        paths = sorted(list(get_data_directory().glob("*.duckdb")))
        return [api.Project(slug=ProjectService._path_to_slug(p), filename=p.name, filepath=str(p)) for p in paths]

    @staticmethod
    def create_idempotent(request: api.CreateProjectRequest) -> api.Project:
        # TODO: should come up with a better way than this to have services point at one another, or remove the need
        from autoarena.service.judge import JudgeService

        data_directory = get_data_directory()
        data_directory.mkdir(parents=True, exist_ok=True)
        path = data_directory / f"{request.name}.duckdb"
        slug = ProjectService._path_to_slug(path)
        ProjectService._setup_database(path)
        JudgeService.create_human_judge(slug)
        return api.Project(slug=slug, filename=path.name, filepath=str(path))

    @staticmethod
    def delete(slug: str) -> None:
        path = ProjectService._slug_to_path(slug)
        path.unlink(missing_ok=True)
        logger.info(f"Removed file '{path}' containing project '{slug}'")

    @staticmethod
    def migrate_all() -> None:
        for project in ProjectService.get_all():
            path = Path(project.filepath)
            ProjectService._setup_database(path)
            logger.info(f"Found project '{path.relative_to(Path.cwd())}'")

    @staticmethod
    def _path_to_slug(path: Path) -> str:
        return path.stem

    @staticmethod
    def _slug_to_path(slug: str) -> Path:
        return get_data_directory() / f"{slug}.duckdb"

    @staticmethod
    def _setup_database(path: Path) -> None:
        ProjectService._migrate_to_latest(path)
        ProjectService._close_pending_tasks(path)

    @staticmethod
    def _migrate_to_latest(path: Path) -> None:
        available_migrations = get_available_migrations()
        applied_migrations = {f for (_, f) in ProjectService._get_applied_migrations(path)}
        for migration in available_migrations:
            if migration.name in applied_migrations:
                continue
            try:
                with get_database_connection(path) as conn:
                    logger.info(f"Applying migration '{migration.name}' to '{path.name}'")
                    conn.sql(migration.read_text())
                    conn.execute(
                        "INSERT INTO migration (migration_index, filename) VALUES ($index, $filename)",
                        dict(index=int(migration.name.split("__")[0]), filename=migration.name),
                    )
            except Exception as e:
                logger.error(f"Failed to apply migration '{migration.name}' to '{path.name}': {e}")
                raise MigrationError(e)

    @staticmethod
    def _get_applied_migrations(path: Path) -> list[tuple[int, str]]:
        try:
            with get_database_connection(path) as conn:
                conn.execute("SELECT migration_index, filename FROM migration ORDER BY migration_index")
                return conn.fetchall()
        except duckdb.CatalogException:
            return []  # database is new and does not have a migration table

    # TODO: restart pending tasks rather than simply terminating
    @staticmethod
    def _close_pending_tasks(path: Path) -> None:
        from autoarena.service.task import TaskService

        slug = ProjectService._path_to_slug(path)
        tasks = TaskService.get_all(slug)
        for task in tasks:
            if task.status not in {api.TaskStatus.COMPLETED, api.TaskStatus.FAILED}:
                TaskService.update(slug, task.id, "Terminated", status=api.TaskStatus.FAILED)
