from __future__ import annotations

from peewee import Model, CharField

from Models import db_proxy


class User(Model):
    token = CharField(unique=True)
    display_name = CharField()

    class Meta:
        database = db_proxy
