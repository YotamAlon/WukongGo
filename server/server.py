import socketio
import eventlet
from peewee import SqliteDatabase
from Models import db_proxy


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
    print(data['game_sgf'])


@sio.event
def move_made(sid, data):
    print(data['move_sgf'])


@sio.event
def disconnect(sid):
    print('disconnected', sid)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
