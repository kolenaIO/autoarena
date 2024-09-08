from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from autoarena.store.utils import setup_database
from autoarena.store import database
from autoarena.main import main, API_V1_STR


@pytest.fixture(scope="function")
def with_empty_database() -> Iterator[None]:
    database_file = Path(__file__).parent / "integration-test.duckdb"
    database_file.unlink(missing_ok=True)
    database.DATABASE_FILE = database_file
    setup_database()
    yield
    database_file.unlink(missing_ok=True)


@pytest.fixture(scope="function")
def api_v1_client(with_empty_database: None) -> Iterator[TestClient]:
    with TestClient(main(), base_url=f"http://testserver{API_V1_STR}") as client:
        yield client
