import abc
import os
import uuid

import tinydb

import config
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
        self._db = tinydb.TinyDB(os.environ[config.DB_FILE_NAME])
        self._table = self._db.table("games")

    def get_game(self, game_id: int) -> Game:
        game_document = self._table.get(doc_id=game_id)
        game = Game.from_sgf(sgf_string=game_document["sgf_string"])
        game.uuid = uuid.UUID(game_document["uuid"])
        return game

    def save_game(self, game: Game) -> int:
        sgf = game.to_sgf()
        game_document = {"sgf_string": str(sgf), "uuid": str(game.id)}
        return self._table.upsert(game_document, tinydb.Query().uuid == str(game.id))[0]
