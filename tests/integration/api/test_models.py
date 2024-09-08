from io import StringIO

import pandas as pd
from fastapi.testclient import TestClient

from autoarena.api import api
from tests.integration.api.conftest import DF_RESULT


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


def test__models__get_ranked_by_judge(api_v1_client: TestClient, project_id: int, model_id: int) -> None: ...  # TODO


def test__models__get_elo_history(api_v1_client: TestClient, model_id: int) -> None: ...


def test__models__get_elo_history__with_judge(api_v1_client: TestClient, model_id: int) -> None: ...


def test__models__download_results_csv(api_v1_client: TestClient, model_id: int) -> None:
    response = api_v1_client.get(f"/model/{model_id}/download/results")
    df_result = pd.read_csv(StringIO(response.text))
    assert df_result[DF_RESULT.columns].equals(DF_RESULT)


def test__models__download_head_to_heads_csv(api_v1_client: TestClient, model_id: int) -> None: ...


def test__models__get_head_to_head_stats(api_v1_client: TestClient, model_id: int) -> None: ...
