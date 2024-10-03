import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from autoarena.store.database import get_database_connection


@pytest.mark.parametrize("n_readers", [2**i for i in range(1, 11)])  # up to 1024
def test__concurrent__read(n_readers: int, test_data_directory: Path) -> None:
    database_file = test_data_directory / "test__concurrent__read.sqlite"
    with get_database_connection(database_file, commit=True) as conn:
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
        conn.execute("INSERT INTO test (value) VALUES ('test')")

    def read() -> list[tuple[int, str]]:
        with get_database_connection(database_file) as conn_reader:  # readonly connections
            return conn_reader.cursor().execute("SELECT id, value FROM test").fetchall()

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=n_readers) as executor:
        futures = [executor.submit(read) for _ in range(n_readers)]

    assert all(f.result() == [(1, "test")] for f in futures)
    assert time.time() - t0 < 5  # should be relatively fast; no blocking or waiting
