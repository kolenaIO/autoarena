from fastapi.testclient import TestClient


def test__head_to_head__get__empty(api_v1_client: TestClient, project_id: int, model_id: int) -> None:
    assert api_v1_client.put("/head-to-heads", json=dict(model_a_id=-1)).json() == []
    assert api_v1_client.put("/head-to-heads", json=dict(model_a_id=model_id)).json() == []


def test__head_to_head__get(api_v1_client: TestClient, project_id: int, model_id: int, model_b_id: int) -> None:
    h2h = api_v1_client.put("/head-to-heads", json=dict(model_a_id=model_id)).json()
    assert len(h2h) == 2
    assert h2h[0]["result_a"]["prompt"] == h2h[0]["result_a"]["prompt"] == "p1"
    assert h2h[0]["result_a"]["response"] == "r1"
    assert h2h[0]["result_b"]["response"] == "b"
    assert h2h[0]["history"] == []
    assert h2h[1]["result_a"]["prompt"] == h2h[1]["result_a"]["prompt"] == "p2"
    assert h2h[1]["result_a"]["response"] == "r2"
    assert h2h[1]["result_b"]["response"] == "bb"
    assert h2h[1]["history"] == []

    # in this case it's the same if you specify model_b_id since there are only two models
    assert api_v1_client.put("/head-to-heads", json=dict(model_a_id=model_id, model_b_id=model_b_id)).json() == h2h

    # same response backwards if other model ID is provided
    h2h_b = api_v1_client.put("/head-to-heads", json=dict(model_a_id=model_b_id)).json()
    for a, b in zip(h2h, h2h_b):
        assert a["result_a"] == b["result_b"]
        assert a["result_b"] == b["result_a"]


def test__head_to_head__submit_judgement(
    api_v1_client: TestClient,
    project_id: int,
    model_id: int,
    model_b_id: int,
) -> None:
    h2h = api_v1_client.put("/head-to-heads", json=dict(model_a_id=model_id, model_b_id=model_b_id)).json()
    result_a_id, result_b_id = h2h[0]["result_a"]["id"], h2h[0]["result_b"]["id"]
    request = dict(project_id=project_id, result_a_id=result_a_id, result_b_id=result_b_id, winner="A")
    assert api_v1_client.post("/head-to-head/judgement", json=request).json() is None
    h2h = api_v1_client.put("/head-to-heads", json=dict(model_a_id=model_id, model_b_id=model_b_id)).json()
    judges = api_v1_client.get(f"/judges/{project_id}").json()
    assert h2h[0]["history"] == [dict(judge_id=judges[0]["id"], judge_name=judges[0]["name"], winner="A")]
    assert h2h[1]["history"] == []

    # if fetched in the other order, the winner is "B"
    h2h = api_v1_client.put("/head-to-heads", json=dict(model_a_id=model_b_id, model_b_id=model_id)).json()
    assert h2h[0]["history"] == [dict(judge_id=judges[0]["id"], judge_name=judges[0]["name"], winner="B")]

    # overwrite previous judgement
    request = dict(project_id=project_id, result_a_id=result_a_id, result_b_id=result_b_id, winner="B")
    assert api_v1_client.post("/head-to-head/judgement", json=request).json() is None
    h2h = api_v1_client.put("/head-to-heads", json=dict(model_a_id=model_id, model_b_id=model_b_id)).json()
    assert h2h[0]["history"] == [dict(judge_id=judges[0]["id"], judge_name=judges[0]["name"], winner="B")]
    assert h2h[1]["history"] == []
