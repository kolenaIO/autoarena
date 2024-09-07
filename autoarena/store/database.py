from contextlib import contextmanager
from pathlib import Path

import duckdb

DATABASE_FILE = Path.cwd() / "autoarena.duckdb"
SCHEMA_FILE = Path(__file__).parent / "schema.sql"


@contextmanager
def get_database_connection(transaction: bool = False) -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(str(DATABASE_FILE))
    try:
        if transaction:
            conn.begin()
        yield conn
        if transaction:
            conn.commit()
    except Exception as e:
        if transaction:
            conn.rollback()
        raise e
    finally:
        conn.close()
