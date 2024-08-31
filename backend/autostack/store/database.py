from contextlib import contextmanager
from pathlib import Path

import duckdb

DATABASE_DIRECTORY = (Path(__file__).parent / ".." / "..").resolve()
DATABASE_FILE = DATABASE_DIRECTORY / "database.duckdb"
SCHEMA_FILE = Path(__file__).parent / "schema.sql"


@contextmanager
def get_database_connection(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(str(DATABASE_FILE), read_only=read_only)
    try:
        yield conn
    finally:
        conn.close()
