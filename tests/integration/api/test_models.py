from fastapi.testclient import TestClient


# TODO: this is one of the more challenging services to test
def test__models(api_v1_client: TestClient, project_id: int) -> None:
    assert api_v1_client.get(f"/models/{project_id}").json() == []
