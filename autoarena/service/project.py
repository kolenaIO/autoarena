import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from loguru import logger

from autoarena.api import api
from autoarena.error import NotFoundError, MigrationError
from autoarena.store.database import get_database_connection, get_available_migrations, DataDirectoryProvider


class ProjectService:
    @staticmethod
    @contextmanager
    def connect(slug: str, commit: bool = False) -> Iterator[sqlite3.Connection]:
        path = ProjectService._slug_to_path(slug)
        if not path.exists():
            raise NotFoundError(f"File for project '{slug}' not found (expected: {path})")
        with get_database_connection(path, commit=commit) as conn:
            yield conn

    @staticmethod
    def get_all() -> list[api.Project]:
        paths = sorted(list(DataDirectoryProvider.get().glob("*.sqlite")))
        return [api.Project(slug=ProjectService._path_to_slug(p), filename=p.name, filepath=str(p)) for p in paths]

    @staticmethod
    def create_idempotent(request: api.CreateProjectRequest) -> api.Project:
        # TODO: should come up with a better way than this to have services point at one another, or remove the need

        data_directory = DataDirectoryProvider.get()
        data_directory.mkdir(parents=True, exist_ok=True)
        path = data_directory / f"{request.name}.sqlite"
        slug = ProjectService._path_to_slug(path)
        ProjectService._setup_database(path)
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
        return DataDirectoryProvider.get() / f"{slug}.sqlite"

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
                with get_database_connection(path, commit=True) as conn:
                    logger.info(f"Applying migration '{migration.name}' to '{path.name}'")
                    cur = conn.cursor()
                    cur.executescript(migration.read_text())
                    cur.execute(
                        "INSERT INTO migration (migration_index, filename) VALUES (:index, :filename)",
                        dict(index=int(migration.name.split("__")[0]), filename=migration.name),
                    )
            except Exception as e:
                logger.error(f"Failed to apply migration '{migration.name}' to '{path.name}': {e}")
                raise MigrationError(e)

    @staticmethod
    def _get_applied_migrations(path: Path) -> list[tuple[int, str]]:
        try:
            with get_database_connection(path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT migration_index, filename FROM migration ORDER BY migration_index")
                return cur.fetchall()
        except sqlite3.OperationalError:
            return []  # database is new and does not have a migration table

    # TODO: restart pending tasks rather than simply terminating
    @staticmethod
    def _close_pending_tasks(path: Path) -> None:
        from autoarena.service.task import TaskService

        slug = ProjectService._path_to_slug(path)
        tasks = TaskService.get_all(slug)
        for task in tasks:
            if task.status not in {api.TaskStatus.COMPLETED, api.TaskStatus.FAILED}:
                logger.warning(f"Terminating stuck '{task.task_type.value}' task with status '{task.status.value}'")
                TaskService.update(slug, task.id, "Terminated", status=api.TaskStatus.FAILED)
