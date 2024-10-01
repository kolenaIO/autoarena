import sqlite3
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Iterator

import pandas as pd

from autoarena.store.utils import id_slug

MIGRATION_DIRECTORY = Path(__file__).parent / "migration"

DataDirectoryProvider: ContextVar[Path] = ContextVar("_DATA_DIRECTORY", default=Path.cwd() / "data")


@contextmanager
def get_database_connection(path: Path, autocommit: bool = False) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(str(path))
    try:
        conn.create_function("id_slug", 2, id_slug)
        conn.cursor().execute("PRAGMA foreign_keys = ON")
        yield conn
    finally:
        if autocommit:
            conn.commit()
        conn.close()


@contextmanager
def temporary_table(conn: sqlite3.Connection, df: pd.DataFrame) -> Iterator[str]:
    table_name = f"tmp_{uuid.uuid4()}".replace("-", "_")
    df.to_sql(table_name, conn, if_exists="fail", index=False)
    try:
        yield table_name
    finally:
        conn.execute(f"DROP TABLE {table_name}")


def get_available_migrations() -> list[Path]:
    return sorted(MIGRATION_DIRECTORY.glob("[0-9][0-9][0-9]__*.sql"))
