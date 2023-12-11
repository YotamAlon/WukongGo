import dataclasses

import fastapi
from fastapi.security import APIKeyHeader

from Models.BasicTypes import Color, MoveType, Point
from Models.Game import Game
from Models.Rule import get_japanese_rule_set
from Models.Timer import Timer
from Models.User import User
from server.repository import GameRepository

API_KEYS = ["94bce547-18f4-4173-b992-1b2dd94e8fc6"]


app = fastapi.FastAPI()


api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def get_api_key(
    api_key: str = fastapi.Security(api_key_header),
) -> str:
    """Retrieve and validate an API key from the query parameters or HTTP header.

    Args:
        api_key: The API key passed in the HTTP header.

    Returns:
        The validated API key.

    Raises:
        HTTPException: If the API key is invalid or missing.
    """
    if api_key in API_KEYS:
        return api_key
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


@app.get("/test")
def test():
    print("connected")
    return "hello :D"


@app.post("/new_game")
def new_game(api_key: str = fastapi.Security(get_api_key)) -> int:
    print("connected using", api_key)
    players = {Color.black: User("black"), Color.white: User("white")}
    game_id = GameRepository().save_game(
        Game.new_game(
            9,
            get_japanese_rule_set(),
            players,
            Timer(),
        )
    )
    return game_id


@dataclasses.dataclass
class MoveSchema:
    type: MoveType
    point: tuple[int, int]


@app.put("/game/{game_id}/make_move")
def make_move(game_id: int, move: MoveSchema, api_key: str = fastapi.Security(get_api_key)):
    game = GameRepository().get_game(int(game_id))
    if move.type is MoveType.play:
        game.make_move(Point(*move.point))
    elif move.type is MoveType.resign:
        game.resign()
    else:
        game.pass_turn()
    GameRepository().save_game(game)


@sio.event
def disconnect(sid):
    print("disconnected", sid)


if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(("", 5000)), app)
