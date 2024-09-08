from fastapi.testclient import TestClient


def test__ui(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "<!doctype html>" in response.text


def test__ui__path(client: TestClient) -> None:
    response = client.get("/project/1/judges")
    assert response.status_code == 200
    assert response.text == client.get("/").text  # any path should return the index, app is client-side routed


def test__ui__assets(client: TestClient) -> None:
    # rather than requiring the assets be built to run this test, just ensure that the asset route is properly 404'ing
    response = client.get("/assets/does-not-exist.jpg")
    assert response.status_code == 404
