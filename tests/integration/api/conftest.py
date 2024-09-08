from io import StringIO

import pandas as pd
import pytest
from fastapi.testclient import TestClient

BASE_CREATE_JUDGE_REQUEST = dict(
    judge_type="ollama",
    name="llama3.1:8b",
    model_name="llama3.1:8b",
    system_prompt="Hello",
    description="Just for testing",
)

DF_RESULT = pd.DataFrame([("p1", "r1"), ("p2", "r2")], columns=["prompt", "response"])
DF_RESULT_B = pd.DataFrame([("p1", "b"), ("p2", "bb"), ("p3", "bbb")], columns=["prompt", "response"])


@pytest.fixture
def project_id(api_v1_client: TestClient) -> int:
    return api_v1_client.put("/project", json=dict(name="test-project")).json()["id"]


@pytest.fixture
def model_id(api_v1_client: TestClient, project_id: int) -> int:
    buf = StringIO()
    DF_RESULT.to_csv(buf, index=False)
    buf.seek(0)
    data = dict(new_model_name="test-model-a", project_id=str(project_id))
    files = dict(file=("example.csv", buf.read()))
    return api_v1_client.post("/model", data=data, files=files).json()["id"]


@pytest.fixture
def model_b_id(api_v1_client: TestClient, project_id: int) -> int:
    buf = StringIO()
    DF_RESULT_B.to_csv(buf, index=False)
    buf.seek(0)
    data = dict(new_model_name="test-model-b", project_id=str(project_id))
    files = dict(file=("example.csv", buf.read()))
    return api_v1_client.post("/model", data=data, files=files).json()["id"]


@pytest.fixture
def judge_id(api_v1_client: TestClient, project_id: int) -> int:
    new_judge_request = dict(project_id=project_id, **BASE_CREATE_JUDGE_REQUEST)
    return api_v1_client.post("/judge", json=new_judge_request).json()["id"]
