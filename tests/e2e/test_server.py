from Models.BasicTypes import Move, Point
from server.endpoints import API_KEYS
from server.repository import GameRepository
from tests.conftest import client


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

    game = GameRepository().get_game(response.json())
    assert game is not None


def test_make_move_endpoint_without_authorization():
    response = client.put(f"/game/1/make_move")
    assert response.status_code == 401


def test_make_move_endpoint():
    response = client.post("/new_game", headers={"Authorization": TEST_API_KEY})
    game_id = response.json()
    response = client.put(
        f"/game/{game_id}/make_move",
        json={"type": "play", "point": [4, 4]},
        headers={"Authorization": TEST_API_KEY},
    )
    assert response.status_code == 200

    game = GameRepository().get_game(game_id)
    assert game.state.last_move == Move.play(Point(4, 4))


def test_make_move_endpoint_with_nonexistent_game():
    response = client.put(
        f"/game/111/make_move",
        json={"type": "play", "point": [4, 4]},
        headers={"Authorization": TEST_API_KEY},
    )
    assert response.status_code == 404


def test_make_same_move_twice_endpoint():
    response = client.post("/new_game", headers={"Authorization": TEST_API_KEY})
    game_id = response.json()
    client.put(
        f"/game/{game_id}/make_move",
        json={"type": "play", "point": [4, 4]},
        headers={"Authorization": TEST_API_KEY},
    )
    response = client.put(
        f"/game/{game_id}/make_move",
        json={"type": "play", "point": [4, 4]},
        headers={"Authorization": TEST_API_KEY},
    )
    assert response.status_code == 400

    game = GameRepository().get_game(game_id)
    assert game.state.last_move == Move.play(Point(4, 4))
    assert game.state.previous_state.previous_state is None
