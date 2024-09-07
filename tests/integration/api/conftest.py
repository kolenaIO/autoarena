import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def project_id(api_v1_client: TestClient) -> int:
    return api_v1_client.put("/project", json=dict(name="test-project")).json()["id"]
