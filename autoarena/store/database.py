import sqlite3
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Iterator

MIGRATION_DIRECTORY = Path(__file__).parent / "migration"

DataDirectoryProvider: ContextVar[Path] = ContextVar("_DATA_DIRECTORY", default=Path.cwd() / "data")


@contextmanager
def get_database_cursor(path: Path) -> Iterator[sqlite3.Cursor]:
    conn = sqlite3.connect(str(path))
    try:
        # TODO: autocommit
        yield conn.cursor()
    finally:
        conn.close()


def get_available_migrations() -> list[Path]:
    return sorted(MIGRATION_DIRECTORY.glob("[0-9][0-9][0-9]__*.sql"))
