from io import StringIO

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from autoarena.api import api
from tests.integration.api.conftest import DF_RESPONSE, DF_RESPONSE_B, construct_upload_model_body


@pytest.fixture
def n_model_a_votes(project_client: TestClient, model_id: int, model_b_id: int) -> int:
    h2h = project_client.put("/head-to-heads", json=dict(model_a_id=model_id, model_b_id=model_b_id)).json()
    for h in h2h:
        request = dict(response_a_id=h["response_a_id"], response_b_id=h["response_b_id"], winner="A")
        assert project_client.post("/head-to-head/vote", json=request).json() is None
    return len(h2h)


def test__models__get__empty(project_client: TestClient) -> None:
    assert project_client.get("/models").json() == []


def test__models__upload(project_client: TestClient, model_id: int) -> None:
    models = project_client.get("/models").json()
    assert len(models) == 1
    assert models[0]["name"] == "test-model-a"
    assert models[0]["n_responses"] == 2
    assert models[0]["n_votes"] == 0


@pytest.mark.parametrize(
    "df_bad,missing",
    [
        (pd.DataFrame.from_records([dict(bad="yes")]), {"prompt", "response"}),
        (pd.DataFrame.from_records([dict(bad="yes", response="ok")]), {"prompt"}),
        (pd.DataFrame.from_records([dict(bad="yes", prompt="what")]), {"response"}),
    ],
)
def test__models__upload__failed(project_client: TestClient, df_bad: pd.DataFrame, missing: set[str]) -> None:
    body = construct_upload_model_body(dict(bad=df_bad))
    response = project_client.post("/model", data=body.data, files=body.files)
    assert response.status_code == 400
    assert f"Missing {len(missing)} required column(s)" in response.json()["detail"]


def test__models__upload__multiple(project_client: TestClient) -> None:
    body = construct_upload_model_body(dict(a=DF_RESPONSE, b=DF_RESPONSE_B))
    models = project_client.post("/model", data=body.data, files=body.files).json()
    assert len(models) == 2
    assert models[0]["name"] == "a"
    assert models[1]["name"] == "b"
    assert models[0]["n_responses"] == len(DF_RESPONSE)
    assert models[1]["n_responses"] == len(DF_RESPONSE_B)
    assert models[0]["n_votes"] == models[1]["n_votes"] == 0


def test__models__get_responses(project_client: TestClient, model_id: int) -> None:
    assert project_client.get(f"/model/{model_id}/responses").json() == [
        api.ModelResponse(prompt="p1", response="r1").__dict__,
        api.ModelResponse(prompt="p2", response="r2").__dict__,
    ]


def test__models__delete(project_client: TestClient, model_id: int) -> None:
    assert len(project_client.get("/models").json()) == 1
    for _ in range(3):  # check idempotence with loop
        assert project_client.delete(f"/model/{model_id}").json() is None
        assert project_client.get("/models").json() == []


def test__models__download_responses_csv(project_client: TestClient, model_id: int) -> None:
    response = project_client.get(f"/model/{model_id}/download/responses")
    df_response = pd.read_csv(StringIO(response.text))
    assert df_response.equals(DF_RESPONSE)


def test__models__download_responses_csv__failed(project_client: TestClient) -> None:
    assert project_client.get("/model/12345/download/responses").status_code == 404


def test__models__trigger_auto_judge(project_client: TestClient, model_id: int) -> None:
    assert project_client.post(f"/model/{model_id}/judge").json() is None
    # TODO: actually check that task is kicked off? requires a configured auto-judge


def test__models__get_ranked_by_judge(
    project_client: TestClient,
    model_id: int,
    model_b_id: int,
    n_model_a_votes: int,
) -> None:
    (human_judge,) = project_client.get("/judges").json()
    models = project_client.get(f"/models/by-judge/{human_judge['id']}").json()
    assert len(models) == n_model_a_votes
    assert models[0]["elo"] > models[1]["elo"]
    for model in models:
        assert model["q025"] is not None
        assert model["q975"] is not None


def test__models__download_head_to_heads_csv(
    project_client: TestClient,
    model_id: int,
    n_model_a_votes: int,
) -> None:
    response = project_client.get(f"/model/{model_id}/download/head-to-heads")
    human_judge_name = project_client.get("/judges").json()[0]["name"]
    df_h2h = pd.read_csv(StringIO(response.text))
    assert set(df_h2h.columns) == {"prompt", "model_a", "model_b", "response_a", "response_b", "judge", "winner"}
    assert len(df_h2h) == n_model_a_votes
    assert all(df_h2h["judge"] == human_judge_name)
    assert all(df_h2h["winner"] == "A")


def test__models__download_head_to_heads_csv__failed(project_client: TestClient) -> None:
    assert project_client.get("/model/12345/download/head-to-heads").status_code == 404


def test__models__get_head_to_head_stats(
    project_client: TestClient,
    model_id: int,
    model_b_id: int,
    n_model_a_votes: int,
) -> None:
    stats = project_client.get(f"/model/{model_id}/head-to-head/stats").json()
    human_judge_id = project_client.get("/judges").json()[0]["id"]
    assert len(stats) == 1  # one opponent, one judge
    assert stats[0]["other_model_id"] == model_b_id
    assert stats[0]["judge_id"] == human_judge_id
    assert stats[0]["count_wins"] == n_model_a_votes
    assert stats[0]["count_losses"] == 0
    assert stats[0]["count_ties"] == 0
