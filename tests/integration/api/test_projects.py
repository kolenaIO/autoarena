from fastapi.testclient import TestClient


def test__projects__empty(api_v1_client: TestClient) -> None:
    assert api_v1_client.get("/projects").json() == []


def test__projects__create(api_v1_client: TestClient) -> None:
    project_name = "test__projects__create"
    new_project_dict = api_v1_client.put("/project", json=dict(name=project_name)).json()
    assert new_project_dict["name"] == project_name
    projects = api_v1_client.get("/projects").json()
    assert len(projects) == 1
    assert new_project_dict == projects[0]

    # creation is idempotent
    assert api_v1_client.put("/project", json=dict(name=project_name)).json() == new_project_dict
    assert len(api_v1_client.get("/projects").json()) == 1


def test__projects__delete(api_v1_client: TestClient) -> None:
    new_project = api_v1_client.put("/project", json=dict(name="test__projects__delete")).json()
    assert api_v1_client.delete(f"/project/{new_project['id']}").json() is None
    assert api_v1_client.get("/projects").json() == []

    # deletion is idempotent
    assert api_v1_client.delete(f"/project/{new_project['id']}").json() is None
    assert api_v1_client.get("/projects").json() == []
