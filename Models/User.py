from peewee import Model, CharField


class User(Model):
    token = CharField()
