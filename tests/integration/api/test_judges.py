import pytest
from fastapi.testclient import TestClient

from tests.integration.api.conftest import CREATE_JUDGE_REQUEST


def test__judges__default_human_judge(project_client: TestClient) -> None:
    default_project_judges = project_client.get("/judges").json()
    assert len(default_project_judges) == 1
    assert default_project_judges[0]["judge_type"] == "human"
    assert default_project_judges[0]["enabled"]
    assert default_project_judges[0]["votes"] == 0


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
    update_request = dict(judge_id=judge_id, enabled=False)
    updated_judge = project_client.put("/judge", json=update_request).json()
    assert updated_judge["enabled"] == update_request["enabled"]

    # update is idempotent
    updated_judge = project_client.put("/judge", json=update_request).json()
    assert updated_judge["enabled"] == update_request["enabled"]


def test__judges__can_access(project_client: TestClient) -> None:
    # just ensure that the API works; full behavior is tested at a lower level than the API
    assert project_client.get("/judge/human/can-access").json()


def test__judges__delete(project_client: TestClient, judge_id: int) -> None:
    assert project_client.delete(f"/judge/{judge_id}").json() is None
    assert len(project_client.get("/judges").json()) == 1  # only default judge is left

    # delete is idempotent
    assert project_client.delete(f"/judge/{judge_id}").json() is None
    assert len(project_client.get("/judges").json()) == 1
