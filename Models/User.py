from peewee import Model, CharField
from Models import db


class User(Model):
    token = CharField()

    class Meta:
        database = db