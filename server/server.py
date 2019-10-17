import socketio
import eventlet
from peewee import SqliteDatabase
from Models import db_proxy
from Models.Game import Game, GameMove, GameUser
from Models.BasicTypes import Move


class WukongoServer(socketio.Server):
    def emit(self, event, data=None, to=None, room=None, skip_sid=None,
             namespace=None, callback=None, **kwargs):
        """Custom event emitter to prevent accidental global event emitting"""
        if to is None and room is None:
            raise ValueError('You must specify a recipient to send the event to')
        super(WukongoServer, self).emit(event, data, to, room, skip_sid, namespace, callback, **kwargs)


sio = WukongoServer()
app = socketio.WSGIApp(sio)

db = SqliteDatabase('wukongo.db')
db_proxy.initialize(db)


@sio.event
def connect(sid, environ):
    print('connected', sid, environ)


@sio.event
def game_started(sid, data):
    game = Game.from_sgf(data['game_sgf'])
    game.save()

    GameUser(game=game, user=game.black).save()
    GameUser(game=game, user=game.white).save()


@sio.event
def move_made(sid, data):
    move = Move.from_sgf(data['move_sgf'])
    move.save()

    GameMove(game=Game.get(uuid=data['game_uuid']), move=move).save()


@sio.event
def disconnect(sid):
    print('disconnected', sid)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
