from peewee import Model
from Models import db_proxy


class Timer(Model):
    pass

    class Meta:
        database = db_proxy