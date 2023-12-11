from fastapi.testclient import TestClient

from server.endpoints import app, API_KEYS

client = TestClient(app)


def test_test_endpoint():
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == "hello :D"


def test_new_game_endpoint_without_authorization():
    response = client.post("/new_game")
    assert response.status_code == 401


TEST_API_KEY = "test-key"
API_KEYS.append(TEST_API_KEY)


def test_game_endpoint():
    response = client.post("/new_game", headers={"Authorization": TEST_API_KEY})
    assert response.status_code == 200
    assert response.json() == 1
