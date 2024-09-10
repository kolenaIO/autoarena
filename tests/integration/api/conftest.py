from io import StringIO

import pandas as pd
import pytest
from fastapi.testclient import TestClient

CREATE_JUDGE_REQUEST = dict(
    judge_type="ollama",
    name="llama3.1:8b",
    model_name="llama3.1:8b",
    system_prompt="Hello",
    description="Just for testing",
)

DF_RESPONSE = pd.DataFrame([("p1", "r1"), ("p2", "r2")], columns=["prompt", "response"])
DF_RESPONSE_B = pd.DataFrame([("p1", "b"), ("p2", "bb"), ("p3", "bbb")], columns=["prompt", "response"])


@pytest.fixture
def model_id(project_client: TestClient) -> int:
    buf = StringIO()
    DF_RESPONSE.to_csv(buf, index=False)
    buf.seek(0)
    data = dict(new_model_name="test-model-a")
    files = dict(file=("example.csv", buf.read()))
    return project_client.post("/model", data=data, files=files).json()["id"]


@pytest.fixture
def model_b_id(project_client: TestClient) -> int:
    buf = StringIO()
    DF_RESPONSE_B.to_csv(buf, index=False)
    buf.seek(0)
    data = dict(new_model_name="test-model-b")
    files = dict(file=("example.csv", buf.read()))
    return project_client.post("/model", data=data, files=files).json()["id"]


@pytest.fixture
def judge_id(project_client: TestClient) -> int:
    return project_client.post("/judge", json=CREATE_JUDGE_REQUEST).json()["id"]
