from contextlib import contextmanager
from pathlib import Path

import duckdb

DATABASE_FILE = Path.cwd() / "autoarena.duckdb"
SCHEMA_FILE = Path(__file__).parent / "schema.sql"


@contextmanager
def get_database_connection() -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(str(DATABASE_FILE))
    try:
        yield conn
    finally:
        conn.close()
