from fastapi.testclient import TestClient


def test__head_to_head__get(api_v1_client: TestClient, project_id: int) -> None:
    request = dict(model_a_id=-1)
    assert api_v1_client.put("/head-to-heads", json=request).json() == []


def test__head_to_head__submit_judgement(api_v1_client: TestClient, project_id: int) -> None:
    request = dict(project_id=project_id, result_a_id=-1, result_b_id=-1, winner="-")
    assert api_v1_client.post("/head-to-head/judgement", json=request).json() is None
