from peewee import Model, CharField
from Models import db_proxy


class User(Model):
    token = CharField()

    class Meta:
        database = db_proxy
