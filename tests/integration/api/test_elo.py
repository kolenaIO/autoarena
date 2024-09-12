from fastapi.testclient import TestClient


# actual functionality is unit tested
def test__elo__reseed(project_client: TestClient) -> None:
    assert project_client.put("/elo/reseed-scores").json() is None
    assert project_client.put("/elo/reseed-scores").json() is None
