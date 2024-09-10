from pathlib import Path

from fastapi.testclient import TestClient

from autoarena.ui_router import ROBOTS_TXT

UI_DIST = Path(__file__).parent / ".." / ".." / "ui" / "dist"


def test__ui(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == (UI_DIST / "index.html").read_text()


def test__ui__path(client: TestClient) -> None:
    response = client.get("/project/1/judges")
    assert response.status_code == 200
    assert response.text == client.get("/").text  # any path should return the index, app is client-side routed


def test__ui__assets(client: TestClient) -> None:
    example_file = next((UI_DIST / "assets").glob("*.jpg"))
    response = client.get(f"/assets/{example_file.name}")
    assert response.status_code == 200
    assert response.content == example_file.read_bytes()


def test__ui__assets__not_found(client: TestClient) -> None:
    response = client.get("/assets/does-not-exist.jpg")
    assert response.status_code == 404


def test__ui__robots(client: TestClient) -> None:
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response.text == ROBOTS_TXT
