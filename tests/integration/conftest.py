import shutil
import uuid
from io import StringIO
from pathlib import Path
from typing import Iterator, Callable

import pytest
from fastapi.testclient import TestClient
from loguru import logger

from autoarena.server import server, API_V1_STR
from autoarena.store.database import set_data_directory


@pytest.fixture(scope="function")
def test_data_directory() -> Iterator[Path]:
    data_directory = Path(__file__).parent / "data"
    data_directory.mkdir(parents=True, exist_ok=True)
    set_data_directory(data_directory)
    try:
        yield data_directory
    finally:
        shutil.rmtree(data_directory, ignore_errors=True)


@pytest.fixture(scope="function")
def log_stream() -> Iterator[Callable[[], str]]:
    logs = StringIO()
    logger.add(logs)

    def get() -> str:
        logs.seek(0)
        return logs.read()

    yield get


@pytest.fixture(scope="function")
def client() -> Iterator[TestClient]:
    with TestClient(server()) as client:
        yield client


@pytest.fixture(scope="function")
def api_v1_client(test_data_directory: Path) -> Iterator[TestClient]:
    with TestClient(server(), base_url=f"http://testserver{API_V1_STR}") as client:
        yield client


@pytest.fixture(scope="function")
def project_slug(api_v1_client: TestClient, test_data_directory: Path) -> Iterator[str]:
    slug = f"test-{str(uuid.uuid4())}"
    database_file = test_data_directory / f"{slug}.duckdb"
    database_file.unlink(missing_ok=True)
    api_v1_client.put("/project", json=dict(name=slug)).json()
    try:
        yield slug
    finally:
        database_file.unlink(missing_ok=True)


@pytest.fixture(scope="function")
def project_client(project_slug: Path) -> Iterator[TestClient]:
    with TestClient(server(), base_url=f"http://testserver{API_V1_STR}/project/{project_slug}") as client:
        yield client
