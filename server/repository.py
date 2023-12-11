import abc
import uuid

import tinydb

from Models.Game import Game


class AbstractGameRepository(abc.ABC):
    @abc.abstractmethod
    def get_game(self, game_id: int) -> Game:
        raise NotImplementedError

    @abc.abstractmethod
    def save_game(self, game: Game) -> int:
        raise NotImplementedError


class GameRepository(AbstractGameRepository):
    def __init__(self):
        self._db = tinydb.TinyDB("wukongo_db.json")
        self._table = self._db.table("games")

    def get_game(self, game_id: int) -> Game:
        game_document = self._table.get(doc_id=game_id)
        game = Game.from_sgf(sgf_string=game_document["sgf_string"])
        game.uuid = uuid.UUID(game_document["uuid"])
        return game

    def save_game(self, game: Game) -> int:
        sgf_string = game.to_sgf()
        game_document = {"sgf_string": sgf_string, "uuid": str(game.uuid)}
        return self._table.upsert(game_document, tinydb.Query().uuid == str(game.uuid))[0]
