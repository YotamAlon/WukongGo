from peewee import Model, TextField


class Rule(Model):
    description = TextField()
