from io import StringIO

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from autoarena.api import api
from tests.integration.api.conftest import DF_RESPONSE


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
    response = project_client.get("/model/12345/download/responses")
    assert response.status_code == 404


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


def test__models__get_elo_history(
    project_client: TestClient,
    model_id: int,
    model_b_id: int,
    n_model_a_votes: int,
) -> None:
    history = project_client.get(f"/model/{model_id}/elo-history").json()
    judges = project_client.get("/judges").json()
    assert len(history) == n_model_a_votes
    assert all(h["other_model_id"] == model_b_id for h in history)
    assert all(h["judge_id"] == judges[0]["id"] for h in history)
    for i in range(1, len(history)):
        assert history[i]["elo"] > history[i - 1]["elo"]  # score should be increasing as all votes are for this model


def test__models__get_elo_history__with_judge(
    project_client: TestClient,
    model_id: int,
    model_b_id: int,
    n_model_a_votes: int,
    judge_id: int,
) -> None:
    history = project_client.get(f"/model/{model_id}/elo-history").json()
    judges = project_client.get("/judges").json()
    params = dict(judge_id=str(judges[0]["id"]))
    history_with_judge = project_client.get(f"/model/{model_id}/elo-history", params=params).json()
    assert history == history_with_judge  # in this case, they're the same, since no other judges have voted

    # no votes, no history
    params = dict(judge_id=str(judge_id))
    assert project_client.get(f"/model/{model_id}/elo-history", params=params).json() == []


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
    response = project_client.get("/model/12345/download/head-to-heads")
    assert response.status_code == 404


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
