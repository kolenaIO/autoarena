import sqlite3
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Iterator

import pandas as pd

from autoarena.store.utils import id_slug, invert_winner

MIGRATION_DIRECTORY = Path(__file__).parent / "migration"

DataDirectoryProvider: ContextVar[Path] = ContextVar("_DATA_DIRECTORY", default=Path.cwd() / "data")


@contextmanager
def get_database_connection(path: Path, commit: bool = False) -> Iterator[sqlite3.Connection]:
    mode = "rwc" if commit else "ro"  # open in readonly mode unless configured to commit
    conn = sqlite3.connect(f"file:{path}?mode={mode}", timeout=10, uri=True)
    cur = conn.cursor()
    try:
        conn.create_function("id_slug", 2, id_slug)
        conn.create_function("invert_winner", 1, invert_winner)
        cur.execute("PRAGMA foreign_keys = ON")
        cur.execute("PRAGMA journal_mode = WAL")
        if commit:
            cur.execute("BEGIN IMMEDIATE TRANSACTION")
        yield conn
        if commit:
            conn.commit()
    except Exception as e:
        if commit:
            conn.rollback()
        raise e
    finally:
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
