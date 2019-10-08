from peewee import Model, CharField
from Models import db_proxy
from typing import List


class User(Model):
    token = CharField(unique=True)
    display_name = CharField()

    class Meta:
        database = db_proxy

    @property
    def games(self) -> List:
        from Models.Game import GameUser
        return list(GameUser.select(GameUser.game).where(GameUser.user == self))

