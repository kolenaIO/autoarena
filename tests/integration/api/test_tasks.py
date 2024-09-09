from fastapi.testclient import TestClient


def test__tasks__get(api_v1_client: TestClient, project_id: int) -> None:
    assert api_v1_client.get(f"/tasks/{project_id}").json() == []
    fine_tune_request = dict(base_model="gemma2:2b")
    assert api_v1_client.post(f"/fine-tune/{project_id}", json=fine_tune_request).json() is None  # create a dummy task
    tasks = api_v1_client.get(f"/tasks/{project_id}").json()
    assert len(tasks) == 1
    assert tasks[0]["task_type"] == "fine-tune"
    assert tasks[0]["progress"] < 1
    assert len(tasks[0]["status"]) > 0


def test__tasks__delete_completed(api_v1_client: TestClient, project_id: int) -> None:
    for _ in range(2):  # loop to check idempotence
        assert api_v1_client.delete(f"/tasks/{project_id}/completed").json() is None
        assert api_v1_client.get(f"/tasks/{project_id}").json() == []
