import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
import json

_connections = set()


def get_online_users(room):
    nicknames = set()
    for channel in _connections:
        if room:
            if channel.room == room:
                nicknames.add(channel.socket.session['nickname'])
        else:
            nicknames.add(channel.socket.session['nickname'])
    return nicknames


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):

    def initialize(self):
        self.logger = logging.getLogger("socketio.chat")
        self.log("Socketio session started")

        _connections.add(self)

        return True

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))
        print "[{0}] {1}".format(self.socket.sessid, message)

    def on_join(self, room):
        #participate of room
        self.log('Joined in room %s' % room)
        self.room = room
        self.join(room)

        nickname = self.request.user.username
        self.socket.session['nickname'] = nickname

        self.broadcast_event('nicknames_in_room', json.dumps(get_online_users(self.room), cls=SetEncoder))

        return True, nickname

    def on_leave(self, room):
        self.log('Leaving in room %s' % room)
        self.room = None
        self.leave(room)

        nickname = self.socket.session['nickname']
        self.broadcast_event('nicknames_in_room', json.dumps(get_online_users(room), cls=SetEncoder))

        print True, nickname

    def on_connect(self):
        self.log('Connecting')

        nickname = self.request.user.username
        self.socket.session['nickname'] = nickname
        self.broadcast_event('announcement', '%s has connected' % nickname)
        self.broadcast_event('nicknames', json.dumps(get_online_users(None), cls=SetEncoder))

        return True

    def recv_disconnect(self):

        # Remove nickname from the list.
        self.log('Disconnected')
        nickname = self.socket.session['nickname']

        _connections.remove(self)
        self.broadcast_event('announcement', '%s has disconnected' % nickname)
        self.broadcast_event('nicknames', json.dumps(get_online_users(None), cls=SetEncoder))

        self.disconnect(silent=False)
        return True

    def on_message(self, msg):
        self.log('User message: {0}'.format(msg))
        self.broadcast_event('refresh_links', True)
        self.emit_to_room(self.room, 'refresh_messages',
            self.socket.session['nickname'], msg)
        return True
