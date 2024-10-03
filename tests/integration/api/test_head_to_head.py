from fastapi.testclient import TestClient


def test__head_to_head__get__empty(project_client: TestClient, model_id: int) -> None:
    assert project_client.put("/head-to-heads", json=dict(model_a_id=-1)).json() == []
    assert project_client.put("/head-to-heads", json=dict(model_a_id=model_id)).json() == []


def test__head_to_head__get(project_client: TestClient, model_id: int, model_b_id: int) -> None:
    h2h = project_client.put("/head-to-heads", json=dict(model_a_id=model_id)).json()
    assert len(h2h) == 2
    assert h2h[0]["prompt"] == "p1"
    assert h2h[0]["response_a"] == "r1"
    assert h2h[0]["response_b"] == "b"
    assert h2h[0]["history"] == []
    assert h2h[1]["prompt"] == "p2"
    assert h2h[1]["response_a"] == "r2"
    assert h2h[1]["response_b"] == "bb"
    assert h2h[1]["history"] == []

    # in this case it's the same if you specify model_b_id since there are only two models
    assert project_client.put("/head-to-heads", json=dict(model_a_id=model_id, model_b_id=model_b_id)).json() == h2h

    # same response backwards if other model ID is provided
    h2h_b = project_client.put("/head-to-heads", json=dict(model_a_id=model_b_id)).json()
    for a, b in zip(h2h, h2h_b):
        assert a["prompt"] == b["prompt"]
        assert a["response_a"] == b["response_b"]
        assert a["response_a_id"] == b["response_b_id"]
        assert a["response_b"] == b["response_a"]
        assert a["response_b_id"] == b["response_a_id"]


def test__head_to_head__submit_vote(project_client: TestClient, model_id: int, model_b_id: int) -> None:
    h2h = project_client.put("/head-to-heads", json=dict(model_a_id=model_id, model_b_id=model_b_id)).json()
    response_a_id, response_b_id = h2h[0]["response_a_id"], h2h[0]["response_b_id"]
    judge_request = dict(response_a_id=response_a_id, response_b_id=response_b_id, winner="A", human_judge_name="human")
    assert project_client.post("/head-to-head/vote", json=judge_request).json() is None
    h2h = project_client.put("/head-to-heads", json=dict(model_a_id=model_id, model_b_id=model_b_id)).json()
    judges = project_client.get("/judges").json()
    assert len(judges) == 1
    assert h2h[0]["history"] == [dict(judge_id=judges[0]["id"], judge_name=judges[0]["name"], winner="A")]
    assert h2h[1]["history"] == []

    # if fetched in the other order, the winner is "B"
    h2h = project_client.put("/head-to-heads", json=dict(model_a_id=model_b_id, model_b_id=model_id)).json()
    assert h2h[0]["history"] == [dict(judge_id=judges[0]["id"], judge_name=judges[0]["name"], winner="B")]

    # overwrite previous vote
    judge_request = dict(response_a_id=response_a_id, response_b_id=response_b_id, winner="B", human_judge_name="human")
    assert project_client.post("/head-to-head/vote", json=judge_request).json() is None
    h2h = project_client.put("/head-to-heads", json=dict(model_a_id=model_id, model_b_id=model_b_id)).json()
    assert h2h[0]["history"] == [dict(judge_id=judges[0]["id"], judge_name=judges[0]["name"], winner="B")]
    assert h2h[1]["history"] == []


def test__head_to_head__submit_vote__with_name(project_client: TestClient, model_id: int, model_b_id: int) -> None:
    h2h = project_client.put("/head-to-heads", json=dict(model_a_id=model_id, model_b_id=model_b_id)).json()
    response_a_id, response_b_id = h2h[0]["response_a_id"], h2h[0]["response_b_id"]
    name = "testuser@example.com"
    judge_request = dict(response_a_id=response_a_id, response_b_id=response_b_id, winner="A", human_judge_name=name)
    assert project_client.post("/head-to-head/vote", json=judge_request).json() is None
    h2h = project_client.put("/head-to-heads", json=dict(model_a_id=model_id, model_b_id=model_b_id)).json()
    judges = project_client.get("/judges").json()
    assert len(judges) == 2
    assert h2h[0]["history"] == [dict(judge_id=judges[1]["id"], judge_name=judges[1]["name"], winner="A")]
    assert h2h[1]["history"] == []


def test__head_to_head__count__2_models(project_client: TestClient, model_id: int, model_b_id: int) -> None:
    assert project_client.get("/head-to-head/count").json() == 2


def test__head_to_head__count__3_models(project_client: TestClient, model_ids: list[int]) -> None:
    assert project_client.get("/head-to-head/count").json() == 5
