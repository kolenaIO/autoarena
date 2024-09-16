import json

from fastapi.testclient import TestClient


def parse_sse_stream(stream: bytes) -> list[dict]:
    return [json.loads(r.split("data: ")[-1]) for r in stream.decode("utf-8").split("\n\n") if r != ""]


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
    response = project_client.get("/tasks/has-active", params=dict(timeout=1.5))
    assert response.status_code == 200
    responses = parse_sse_stream(response.read())
    assert len(responses) == 1  # should only yield one message as the answer does not change in the timeout period
    assert responses[0] == dict(has_active=False)


def test__tasks__get_stream(project_client: TestClient, model_ids: list[int]) -> None:
    assert project_client.delete(f"/model/{model_ids[0]}").json() is None  # kicks off a leaderboard recompute
    tasks = project_client.get("/tasks").json()
    assert len(tasks) == 1
    task_stream = project_client.get(f"/task/{tasks[0]['id']}/stream")
    responses = parse_sse_stream(task_stream.read())
    assert len(responses) == 1
    assert responses[0] == tasks[0]


def test__tasks__delete_completed(project_client: TestClient) -> None:
    for _ in range(2):  # loop to check idempotence
        assert project_client.delete("/tasks/completed").json() is None
        assert project_client.get("/tasks").json() == []
