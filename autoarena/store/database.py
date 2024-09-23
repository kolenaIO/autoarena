from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

import duckdb

DATABASE_FILE = Path.cwd() / "autoarena.duckdb"
MIGRATION_DIRECTORY = Path(__file__).parent / "migration"

DataDirectoryProvider: ContextVar[Path] = ContextVar("_DATA_DIRECTORY", default=Path.cwd() / "data")


@contextmanager
def get_database_connection(path: Path) -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(str(path))
    try:
        yield conn
    finally:
        conn.close()


def get_available_migrations() -> list[Path]:
    return sorted(MIGRATION_DIRECTORY.glob("[0-9][0-9][0-9]__*.sql"))
