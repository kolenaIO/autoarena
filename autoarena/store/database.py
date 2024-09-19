from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Iterator

import duckdb

DATABASE_FILE = Path.cwd() / "autoarena.duckdb"
MIGRATION_DIRECTORY = Path(__file__).parent / "migration"

_DATA_DIRECTORY: ContextVar[Path] = ContextVar("_DATA_DIRECTORY", default=Path.cwd() / "data")


@contextmanager
def data_directory(directory: Path) -> Iterator[Path]:
    original = _DATA_DIRECTORY.set(directory)
    try:
        yield directory
    finally:
        _DATA_DIRECTORY.reset(original)


@contextmanager
def tenant_data_directory(tenant: str) -> Iterator[Path]:
    base_path = _DATA_DIRECTORY.get()
    tenant_path = base_path / tenant
    with data_directory(tenant_path) as p:
        yield p


def get_data_directory() -> Path:
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
