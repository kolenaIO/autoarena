import json

from fastapi.testclient import TestClient


def test__tasks__get(project_client: TestClient) -> None:
    assert project_client.get("/tasks").json() == []
    fine_tune_request = dict(base_model="gemma2:2b")
    assert project_client.post("/fine-tune", json=fine_tune_request).json() is None  # dummy
    tasks = project_client.get("/tasks").json()
    assert len(tasks) == 1
    assert tasks[0]["task_type"] == "fine-tune"
    assert tasks[0]["progress"] < 1
    assert len(tasks[0]["status"]) > 0


def test__tasks__has_active(project_client: TestClient) -> None:
    requested_event_count = 2
    response = project_client.get("/tasks/has-active", params=dict(maximum=requested_event_count))
    assert response.status_code == 200
    responses = [r.split("data: ")[-1] for r in response.read().decode("utf-8").split("\n\n") if r != ""]
    assert len(responses) == requested_event_count
    assert all(json.loads(r) == dict(has_active=False) for r in responses)


def test__tasks__delete_completed(project_client: TestClient) -> None:
    for _ in range(2):  # loop to check idempotence
        assert project_client.delete("/tasks/completed").json() is None
        assert project_client.get("/tasks").json() == []
