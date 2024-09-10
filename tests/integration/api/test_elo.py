from fastapi.testclient import TestClient


# TODO: actually test functionality, probably at a lower level than this
def test__elo__reseed(project_client: TestClient) -> None:
    assert project_client.put("/elo/reseed-scores").json() is None
    assert project_client.put("/elo/reseed-scores").json() is None
