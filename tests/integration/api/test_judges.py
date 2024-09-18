from io import StringIO

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from tests.integration.api.conftest import CREATE_JUDGE_REQUEST


def test__judges__default_human_judge(project_client: TestClient) -> None:
    default_project_judges = project_client.get("/judges").json()
    assert len(default_project_judges) == 1
    assert default_project_judges[0]["judge_type"] == "human"
    assert default_project_judges[0]["enabled"]
    assert default_project_judges[0]["n_votes"] == 0


def test__judges__default_system_prompt(project_client: TestClient) -> None:
    default_system_prompt = project_client.get("/judge/default-system-prompt").json()
    assert type(default_system_prompt) is str
    assert len(default_system_prompt) > 0


def test__judges__create(project_client: TestClient) -> None:
    new_judge_dict = project_client.post("/judge", json=CREATE_JUDGE_REQUEST).json()
    for key in ["judge_type", "name", "model_name", "system_prompt", "description"]:
        assert new_judge_dict[key] == CREATE_JUDGE_REQUEST[key]
    assert project_client.get("/judges").json()[1] == new_judge_dict

    # create is not idempotent (POST)
    with pytest.raises(Exception):
        project_client.post("/judge", json=CREATE_JUDGE_REQUEST).json()


def test__judges__update(project_client: TestClient, judge_id: int) -> None:
    existing = project_client.get("/judges").json()[-1]
    assert existing["id"] == judge_id
    assert existing["enabled"]

    updated_judge = project_client.put(f"/judge/{judge_id}", json=dict(enabled=False)).json()
    assert not updated_judge["enabled"]

    # update is idempotent
    updated_judge = project_client.put(f"/judge/{judge_id}", json=dict(enabled=False)).json()
    assert not updated_judge["enabled"]


def test__judges__can_access__human(project_client: TestClient) -> None:
    # just ensure that the API works; full behavior is tested at a lower level than the API
    assert project_client.get("/judge/human/can-access").json()


def test__judges__can_access__unrecognized__failed(project_client: TestClient) -> None:
    assert not project_client.get("/judge/unrecognized/can-access").json()


def test__judges__download_votes_csv(project_client: TestClient, model_id: int, model_b_id: int) -> None:
    h2h = project_client.put("/head-to-heads", json=dict(model_a_id=model_id, model_b_id=model_b_id)).json()
    judge_request = dict(response_a_id=h2h[0]["response_a_id"], response_b_id=h2h[0]["response_b_id"], winner="A")
    assert project_client.post("/head-to-head/vote", json=judge_request).json() is None
    judge_request = dict(response_a_id=h2h[1]["response_b_id"], response_b_id=h2h[1]["response_a_id"], winner="-")
    assert project_client.post("/head-to-head/vote", json=judge_request).json() is None
    judges = project_client.get("/judges").json()
    assert len(judges) == 1
    assert judges[0]["n_votes"] == 2
    human_judge_id = judges[0]["id"]
    response = project_client.get(f"/judge/{human_judge_id}/download/votes")
    assert response.status_code == 200
    models = project_client.get("/models").json()
    assert len(models) == 2
    model_a, model_b = [m for m in models if m["id"] == model_id][0], [m for m in models if m["id"] == model_b_id][0]
    df_vote_expected = pd.DataFrame(
        [
            (h2h[0]["prompt"], model_a["name"], model_b["name"], h2h[0]["response_a"], h2h[0]["response_b"], "A"),
            (h2h[1]["prompt"], model_b["name"], model_a["name"], h2h[1]["response_b"], h2h[1]["response_a"], "-"),
        ],
        columns=["prompt", "model_a", "model_b", "response_a", "response_b", "winner"],
    )
    df_vote = pd.read_csv(StringIO(response.text))
    assert df_vote.equals(df_vote_expected)


def test__judges__delete(project_client: TestClient, judge_id: int) -> None:
    assert project_client.delete(f"/judge/{judge_id}").json() is None
    assert len(project_client.get("/judges").json()) == 1  # only default judge is left

    # delete is idempotent
    assert project_client.delete(f"/judge/{judge_id}").json() is None
    assert len(project_client.get("/judges").json()) == 1
