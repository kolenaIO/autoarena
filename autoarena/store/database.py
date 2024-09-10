from contextlib import contextmanager
from pathlib import Path

import duckdb

DATABASE_FILE = Path.cwd() / "autoarena.duckdb"
MIGRATION_DIRECTORY = Path(__file__).parent / "migration"

_DATA_DIRECTORY = Path.cwd() / "data"


def get_data_directory() -> Path:
    return _DATA_DIRECTORY


# TODO: allow command line updates? e.g. --data-dir ./my-data
def set_data_directory(path: Path) -> None:
    global _DATA_DIRECTORY
    _DATA_DIRECTORY = path


@contextmanager
def get_database_connection(path: Path) -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(str(path))
    try:
        yield conn
    finally:
        conn.close()


def get_available_migrations() -> list[Path]:
    return sorted(MIGRATION_DIRECTORY.glob("[0-9][0-9][0-9]__*.sql"))
