from Models.BasicTypes import Point, Score, Move
from Models import db_proxy
from peewee import SqliteDatabase


DATABASE = 'testing.db'
db = SqliteDatabase(DATABASE)
db_proxy.initialize(db)
db.connect()

db.create_tables([Point, Score, Move])
point = Point.create(row=3, col=5)
print(point)
print(Score.create(w_score=6.5, b_score=0))
print(Move.play(point))
# print(Move.resign())
# print(Move.pass_turn())

db.close()
