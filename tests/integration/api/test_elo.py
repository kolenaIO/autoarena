from fastapi.testclient import TestClient


# TODO: actually test functionality, probably at a lower level than this
def test__elo__reseed(api_v1_client: TestClient, project_id: int) -> None:
    assert api_v1_client.put(f"/elo/reseed-scores/{project_id}").json() is None
    assert api_v1_client.put(f"/elo/reseed-scores/{project_id}").json() is None
