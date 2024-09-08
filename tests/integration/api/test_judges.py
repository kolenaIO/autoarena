import pytest
from fastapi.testclient import TestClient

from tests.integration.api.conftest import BASE_CREATE_JUDGE_REQUEST


def test__judges__default_human_judge(api_v1_client: TestClient, project_id: int) -> None:
    default_project_judges = api_v1_client.get(f"/judges/{project_id}").json()
    assert len(default_project_judges) == 1
    assert default_project_judges[0]["judge_type"] == "human"
    assert default_project_judges[0]["enabled"]
    assert default_project_judges[0]["votes"] == 0


def test__judges__default_system_prompt(api_v1_client: TestClient, project_id: int) -> None:
    default_system_prompt = api_v1_client.get("/judge/default-system-prompt").json()
    assert type(default_system_prompt) is str
    assert len(default_system_prompt) > 0


def test__judges__create(api_v1_client: TestClient, project_id: int) -> None:
    new_judge_request = dict(project_id=project_id, **BASE_CREATE_JUDGE_REQUEST)
    new_judge_dict = api_v1_client.post("/judge", json=new_judge_request).json()
    for key in ["judge_type", "name", "model_name", "system_prompt", "description"]:
        assert new_judge_dict[key] == new_judge_request[key]
    assert api_v1_client.get(f"/judges/{project_id}").json()[1] == new_judge_dict

    # create is not idempotent (POST)
    with pytest.raises(Exception):
        api_v1_client.post("/judge", json=new_judge_request).json()


def test__judges__update(api_v1_client: TestClient, project_id: int, judge_id: int) -> None:
    update_request = dict(project_id=project_id, judge_id=judge_id, enabled=False)
    updated_judge = api_v1_client.put("/judge", json=update_request).json()
    assert updated_judge["enabled"] == update_request["enabled"]

    # update is idempotent
    assert api_v1_client.put("/judge", json=update_request).json()["enabled"] == update_request["enabled"]


def test__judges__can_access(api_v1_client: TestClient, project_id: int) -> None:
    # just ensure that the API works; full behavior is tested at a lower level than the API
    assert api_v1_client.get("/judge/human/can-access").json()


def test__judges__delete(api_v1_client: TestClient, project_id: int, judge_id: int) -> None:
    assert api_v1_client.delete(f"/judge/{judge_id}").json() is None
    assert len(api_v1_client.get(f"/judges/{project_id}").json()) == 1  # only default judge is left

    # delete is idempotent
    assert api_v1_client.delete(f"/judge/{judge_id}").json() is None
    assert len(api_v1_client.get(f"/judges/{project_id}").json()) == 1
