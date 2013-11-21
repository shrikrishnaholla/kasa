# Credits Rick Copeland
# http://sourceforge.net/u/rick446/pygotham

import os

from socketio import socketio_manage
from socketio.server import SocketIOServer

from socketio.namespace import BaseNamespace

import spamfilter

public = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'public'))

PORT = 8080

class ChatNamespace(BaseNamespace):
    _registry = {}

    def initialize(self):
        self._registry[id(self)] = self
        self.emit('connect')
        self.nick = None

    def disconnect(self, *args, **kwargs):
        if self.nick:
            self._broadcast('exit', self.nick)
        del self._registry[id(self)]
        super(ChatNamespace, self).disconnect(*args, **kwargs)

    def on_login(self, nick):
        if self.nick:
            self._broadcast('exit', self.nick)
        self.nick = nick
        self._broadcast('enter', nick)
        self.emit('users',
                  [ ns.nick
                    for ns in self._registry.values()
                    if ns.nick is not None ])

    def on_chat(self, message):
        if self.nick:
            self._broadcast('chat', dict(u=self.nick, m=message, s=spamfilter.isSpam(message).__str__()))
        else:
            self.emit('chat', dict(u='SYSTEM', m='You must first login', s='False'))

    def _broadcast(self, event, message):
        for s in self._registry.values():
            s.emit(event, message)


def chat(environ, start_response):
    if environ['PATH_INFO'].startswith('/socket.io'):
        return socketio_manage(environ, { '/chat': ChatNamespace })
    else:
        return serve_file(environ, start_response)

def serve_file(environ, start_response):
    path = os.path.normpath(
        os.path.join(public, environ['PATH_INFO'].lstrip('/')))
    if environ['PATH_INFO'] == '/':
        path += '/chat.html'
    assert path.startswith(public), path
    if os.path.exists(path):
        start_response('200 OK', [('Content-Type', 'text/html')])
        with open(path) as fp:
            while True:
                chunk = fp.read(4096)
                if not chunk: break
                yield chunk
    else:
        start_response('404 NOT FOUND', [])
        yield 'File not found'

sio_server = SocketIOServer(
    ('', PORT), chat, 
    policy_server=False)

print 'Server is running on http://0.0.0.0:' + PORT.__str__()

try:
    sio_server.serve_forever()
except KeyboardInterrupt:
    print '\nStopping Server...'