import datetime
import shutil
import uuid
from io import StringIO
from pathlib import Path
from typing import Iterator, Callable, Union

import pytest
from fastapi.testclient import TestClient
from loguru import logger

from autoarena.server import server, API_V1_STR
from autoarena.store.database import DataDirectoryProvider


@pytest.fixture(scope="function")
def test_data_directory() -> Iterator[Path]:
    test_data_dir = Path(__file__).parent / "data"
    test_data_dir.mkdir(parents=True, exist_ok=True)
    try:
        DataDirectoryProvider.set(test_data_dir)
        yield test_data_dir
    finally:
        shutil.rmtree(test_data_dir, ignore_errors=True)


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
    database_file = test_data_directory / f"{slug}.sqlite"
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


def assert_recent(timestamp: Union[datetime.datetime, str]) -> None:
    if isinstance(timestamp, str):
        if timestamp.endswith("Z"):
            timestamp = timestamp[:-1] + "+00:00"  # Python <=3.10 doesn't like 'Z' as a UTC indicator
        timestamp = datetime.datetime.fromisoformat(timestamp)
    now = datetime.datetime.now(datetime.timezone.utc)  # use datetime.timezone instead of datetime.UTC for <=3.10
    ten_seconds_ago = now - datetime.timedelta(seconds=10)
    assert ten_seconds_ago < timestamp < now
