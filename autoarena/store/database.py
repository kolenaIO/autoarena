from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Iterator

import duckdb

DATABASE_FILE = Path.cwd() / "autoarena.duckdb"
MIGRATION_DIRECTORY = Path(__file__).parent / "migration"

_DATA_DIRECTORY: ContextVar[Path] = ContextVar("_DATA_DIRECTORY", default=Path.cwd() / "data")


class DataDirectoryProvider:
    @staticmethod
    @contextmanager
    def set(directory: Path) -> Iterator[Path]:
        original = _DATA_DIRECTORY.set(directory)
        try:
            yield directory
        finally:
            _DATA_DIRECTORY.reset(original)

    @staticmethod
    def get() -> Path:
        return _DATA_DIRECTORY.get()


@contextmanager
def get_database_connection(path: Path) -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(str(path))
    try:
        yield conn
    finally:
        conn.close()


def get_available_migrations() -> list[Path]:
    return sorted(MIGRATION_DIRECTORY.glob("[0-9][0-9][0-9]__*.sql"))
