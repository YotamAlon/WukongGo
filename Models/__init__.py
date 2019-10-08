from peewee import DatabaseProxy, Database


class WukongoDB(DatabaseProxy):
    def initialize(self, obj: Database):
        super(WukongoDB, self).initialize(obj)
        if obj is not None:
            # Importing the models at runtime to avoid circular import issue
            from Models.User import User
            from Models.BasicTypes import Move
            from Models.Game import Game, GameMove, GameUser

            obj.create_tables([User, Move, Game, GameMove, GameUser])


db_proxy = WukongoDB()
