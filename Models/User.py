from peewee import Model, CharField
from Models import db_proxy
from Models.Game import GameUser, Game
from typing import List


class User(Model):
    token = CharField()
    display_name = CharField()

    class Meta:
        db = db_proxy

    @property
    def games(self) -> List[Game]:
        return list(GameUser.select(GameUser.game).where(GameUser.user == self))

