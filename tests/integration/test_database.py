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


# up to 32 writers, 512 readers
@pytest.mark.parametrize("n_writers, n_readers", [(2**i, 2 ** (i + 4)) for i in range(1, 6)])
def test__concurrent__write(n_writers: int, n_readers: int, test_data_directory: Path) -> None:
    database_file = test_data_directory / "test__concurrent__write.sqlite"
    with get_database_connection(database_file, commit=True) as conn:
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT UNIQUE)")
        conn.execute("INSERT INTO test (value) VALUES ('test')")

    def read() -> list[tuple[str]]:
        with get_database_connection(database_file) as conn_reader:
            return conn_reader.cursor().execute("SELECT value FROM test WHERE id = 1").fetchall()

    def write() -> None:
        with get_database_connection(database_file, commit=True) as conn_writer:
            conn_writer.cursor().execute("INSERT INTO test (value) VALUES ('concurrent-' || hex(randomblob(32)))")

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=n_writers + n_readers) as executor:
        readers = [executor.submit(read) for _ in range(n_readers)]
        writers = [executor.submit(write) for _ in range(n_writers)]

    assert all(f.result() == [("test",)] for f in readers)
    assert all(f.result() is None for f in writers)
    assert time.time() - t0 < 5  # should be relatively fast; not much waiting

    with get_database_connection(database_file) as conn:
        assert conn.cursor().execute("SELECT COUNT(*) FROM test").fetchone() == (1 + n_writers,)
