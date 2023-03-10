from __future__ import annotations

from peewee import Model, CharField

from Models import db_proxy
from Models.Game import GameUser


class User(Model):
    token = CharField(unique=True)
    display_name = CharField()

    class Meta:
        database = db_proxy

    @property
    def games(self) -> list[GameUser]:
        return list(GameUser.select(GameUser.game).where(GameUser.user == self))
