from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import duckdb
from coolname import generate_slug

DATABASE_DIRECTORY = (Path(__file__).parent / ".." / ".data").resolve()
DATABASE_FILE = DATABASE_DIRECTORY / "database.duckdb"


@contextmanager
def get_database_connection() -> Iterator[duckdb.DuckDBPyConnection]:
    conn = duckdb.connect(str(DATABASE_FILE))
    try:
        yield conn
    finally:
        conn.close()


def migrate_database(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("CREATE SEQUENCE IF NOT EXISTS model_id START 1")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS model (
            id INTEGER PRIMARY KEY DEFAULT nextval('model_id'),
            name TEXT NOT NULL,
        )
    """)
    conn.execute(
        """
        INSERT INTO model(name) VALUES (?), (?), (?)
    """,
        [generate_slug(2) for _ in range(3)],
    )


def setup_database() -> None:
    DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    with get_database_connection() as conn:
        migrate_database(conn)
