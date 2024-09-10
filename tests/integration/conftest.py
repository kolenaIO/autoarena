import shutil
import uuid
from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from autoarena.main import main, API_V1_STR
from autoarena.store.database import set_data_directory


@pytest.fixture(scope="session")
def test_data_directory() -> Iterator[Path]:
    data_directory = Path(__file__).parent / "data"
    set_data_directory(data_directory)
    try:
        yield data_directory
    finally:
        shutil.rmtree(data_directory, ignore_errors=True)


@pytest.fixture(scope="function")
def client() -> Iterator[TestClient]:
    with TestClient(main()) as client:
        yield client


@pytest.fixture(scope="function")
def api_v1_client(test_data_directory: Path) -> Iterator[TestClient]:
    with TestClient(main(), base_url=f"http://testserver{API_V1_STR}") as client:
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
    with TestClient(main(), base_url=f"http://testserver{API_V1_STR}/project/{project_slug}") as client:
        yield client
