from io import StringIO

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from autoarena.api import api
from tests.integration.api.conftest import DF_RESULT


@pytest.fixture
def n_model_a_votes(api_v1_client: TestClient, project_id: int, model_id: int, model_b_id: int) -> int:
    h2h = api_v1_client.put("/head-to-heads", json=dict(model_a_id=model_id, model_b_id=model_b_id)).json()
    for h in h2h:
        request = dict(project_id=project_id, result_a_id=h["result_a_id"], result_b_id=h["result_b_id"], winner="A")
        assert api_v1_client.post("/head-to-head/judgement", json=request).json() is None
    return len(h2h)


def test__models__get__empty(api_v1_client: TestClient, project_id: int) -> None:
    assert api_v1_client.get(f"/models/{project_id}").json() == []
    assert api_v1_client.get("/models/-1").json() == []


def test__models__upload(api_v1_client: TestClient, project_id: int, model_id: int) -> None:
    models = api_v1_client.get(f"/models/{project_id}").json()
    assert len(models) == 1
    assert models[0]["name"] == "test-model-a"
    assert models[0]["datapoints"] == 2
    assert models[0]["votes"] == 0


def test__models__get_results(api_v1_client: TestClient, project_id: int, model_id: int) -> None:
    assert api_v1_client.get(f"/model/{model_id}/results").json() == [
        api.ModelResult(prompt="p1", response="r1").__dict__,
        api.ModelResult(prompt="p2", response="r2").__dict__,
    ]


def test__models__delete(api_v1_client: TestClient, project_id: int, model_id: int) -> None:
    assert len(api_v1_client.get(f"/models/{project_id}").json()) == 1
    for _ in range(3):  # check idempotence with loop
        assert api_v1_client.delete(f"/model/{model_id}").json() is None
        assert api_v1_client.get(f"/models/{project_id}").json() == []


def test__models__download_results_csv(api_v1_client: TestClient, model_id: int) -> None:
    response = api_v1_client.get(f"/model/{model_id}/download/results")
    df_result = pd.read_csv(StringIO(response.text))
    assert df_result[DF_RESULT.columns].equals(DF_RESULT)


def test__models__trigger_judgement(api_v1_client: TestClient, model_id: int) -> None:
    assert api_v1_client.post(f"/model/{model_id}/judge").json() is None
    # TODO: actually check that task is kicked off? requires a configured auto-judge


def test__models__get_ranked_by_judge(
    api_v1_client: TestClient,
    project_id: int,
    model_id: int,
    model_b_id: int,
    n_model_a_votes: int,
) -> None:
    (human_judge,) = api_v1_client.get(f"/judges/{project_id}").json()
    models = api_v1_client.get(f"/models/{project_id}/by-judge/{human_judge['id']}").json()
    assert len(models) == n_model_a_votes
    assert models[0]["elo"] > models[1]["elo"]
    for model in models:
        assert model["q025"] is not None
        assert model["q975"] is not None


def test__models__get_elo_history(
    api_v1_client: TestClient,
    project_id: int,
    model_id: int,
    model_b_id: int,
    n_model_a_votes: int,
) -> None:
    history = api_v1_client.get(f"/model/{model_id}/elo-history").json()
    judges = api_v1_client.get(f"/judges/{project_id}").json()
    assert len(history) == n_model_a_votes
    assert all(h["other_model_id"] == model_b_id for h in history)
    assert all(h["judge_id"] == judges[0]["id"] for h in history)
    for i in range(1, len(history)):
        assert history[i]["elo"] > history[i - 1]["elo"]  # score should be increasing as all votes are for this model


def test__models__get_elo_history__with_judge(
    api_v1_client: TestClient,
    project_id: int,
    model_id: int,
    model_b_id: int,
    n_model_a_votes: int,
    judge_id: int,
) -> None:
    history = api_v1_client.get(f"/model/{model_id}/elo-history").json()
    judges = api_v1_client.get(f"/judges/{project_id}").json()
    params = dict(judge_id=str(judges[0]["id"]))
    history_with_judge = api_v1_client.get(f"/model/{model_id}/elo-history", params=params).json()
    assert history == history_with_judge  # in this case, they're the same, since no other judges have voted

    # no votes, no history
    params = dict(judge_id=str(judge_id))
    assert api_v1_client.get(f"/model/{model_id}/elo-history", params=params).json() == []


def test__models__download_head_to_heads_csv(
    api_v1_client: TestClient,
    project_id: int,
    model_id: int,
    n_model_a_votes: int,
) -> None:
    response = api_v1_client.get(f"/model/{model_id}/download/head-to-heads")
    human_judge_name = api_v1_client.get(f"/judges/{project_id}").json()[0]["name"]
    df_h2h = pd.read_csv(StringIO(response.text))
    assert len(df_h2h) == n_model_a_votes
    assert all(df_h2h["judge"] == human_judge_name)
    assert all(df_h2h["winner"] == "A")


def test__models__get_head_to_head_stats(
    api_v1_client: TestClient,
    project_id: int,
    model_id: int,
    model_b_id: int,
    n_model_a_votes: int,
) -> None:
    stats = api_v1_client.get(f"/model/{model_id}/head-to-head/stats").json()
    human_judge_id = api_v1_client.get(f"/judges/{project_id}").json()[0]["id"]
    assert len(stats) == 1  # one opponent, one judge
    assert stats[0]["other_model_id"] == model_b_id
    assert stats[0]["judge_id"] == human_judge_id
    assert stats[0]["count_wins"] == n_model_a_votes
    assert stats[0]["count_losses"] == 0
    assert stats[0]["count_ties"] == 0
