from fastapi.testclient import TestClient


def test__tasks__get(api_v1_client: TestClient, project_slug: str) -> None:
    assert api_v1_client.get(f"/project/{project_slug}/tasks").json() == []
    fine_tune_request = dict(base_model="gemma2:2b")
    assert api_v1_client.post(f"/project/{project_slug}/fine-tune", json=fine_tune_request).json() is None  # dummy
    tasks = api_v1_client.get(f"/project/{project_slug}/tasks").json()
    assert len(tasks) == 1
    assert tasks[0]["task_type"] == "fine-tune"
    assert tasks[0]["progress"] < 1
    assert len(tasks[0]["status"]) > 0


def test__tasks__delete_completed(api_v1_client: TestClient, project_slug: str) -> None:
    for _ in range(2):  # loop to check idempotence
        assert api_v1_client.delete(f"/project/{project_slug}/tasks/completed").json() is None
        assert api_v1_client.get(f"/project/{project_slug}/tasks").json() == []
