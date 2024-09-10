from io import StringIO

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from pydantic.dataclasses import dataclass

CREATE_JUDGE_REQUEST = dict(
    judge_type="ollama",
    name="llama3.1:8b",
    model_name="llama3.1:8b",
    system_prompt="Hello",
    description="Just for testing",
)

DF_RESPONSE = pd.DataFrame([("p1", "r1"), ("p2", "r2")], columns=["prompt", "response"])
DF_RESPONSE_B = pd.DataFrame([("p1", "b"), ("p2", "bb"), ("p3", "bbb")], columns=["prompt", "response"])


@dataclass(frozen=True)
class UploadModelBody:
    data: dict[str, str]
    files: dict[str, tuple[str, str]]


def construct_upload_model_body(model_name_to_df: dict[str, pd.DataFrame]) -> UploadModelBody:
    model_names = list(model_name_to_df.keys())
    filenames = [f"{model_name}.csv" for model_name in model_names]
    buffers = []
    for model_name in model_names:
        buf = StringIO()
        model_name_to_df[model_name].to_csv(buf, index=False)
        buf.seek(0)
        buffers.append(buf)
    return UploadModelBody(
        data={f"{filename}||model_name": model_name for filename, model_name in zip(filenames, model_names)},
        files={filename: (filename, buf.read()) for filename, buf in zip(filenames, buffers)},
    )


@pytest.fixture
def model_id(project_client: TestClient) -> int:
    body = construct_upload_model_body({"test-model-a": DF_RESPONSE})
    return project_client.post("/model", data=body.data, files=body.files).json()[0]["id"]


@pytest.fixture
def model_b_id(project_client: TestClient) -> int:
    body = construct_upload_model_body({"test-model-b": DF_RESPONSE_B})
    return project_client.post("/model", data=body.data, files=body.files).json()[0]["id"]


@pytest.fixture
def judge_id(project_client: TestClient) -> int:
    return project_client.post("/judge", json=CREATE_JUDGE_REQUEST).json()["id"]
