from fastapi.testclient import TestClient


def test__projects__empty(api_v1_client: TestClient) -> None:
    assert api_v1_client.get("/projects").json() == []


def test__projects__create(api_v1_client: TestClient, project_slug: str) -> None:
    # this is created (and deleted) by the fixture; assert that it is created correctly
    projects = api_v1_client.get("/projects").json()
    assert len(projects) == 1
    assert project_slug == projects[0]["slug"]

    # creation is idempotent
    new_project_dict = api_v1_client.put("/project", json=dict(name=project_slug)).json()
    assert new_project_dict["slug"] == project_slug
    assert api_v1_client.get("/projects").json() == projects


def test__projects__delete(api_v1_client: TestClient, project_slug: str) -> None:
    assert api_v1_client.delete(f"/project/{project_slug}").json() is None
    assert api_v1_client.get("/projects").json() == []

    # deletion is idempotent
    assert api_v1_client.delete(f"/project/{project_slug}").json() is None
    assert api_v1_client.get("/projects").json() == []
