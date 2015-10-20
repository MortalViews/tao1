import sys, os, time, asyncio, jinja2, aiohttp_jinja2, json, traceback, pickle
from uuid import uuid4
from aiohttp import web
import aiohttp
from aiohttp.web import Application, Response, MsgType, WebSocketResponse
from core.union import response_json
import settings
from settings import *
from collections import defaultdict


# rooms = defaultdict(list)
# players = rooms[msg.room]


class Player(list):
    last_id = 0
    __slot__ = []

    def __init__(self, client, room, x=0, y=0, z=0, a=0, b=0):
        assert isinstance(client, web.WebSocketResponse)
        assert isinstance(room, Room)
        list.__init__(self, (x, y, z, a, b))
        # клиент и комната, к которым относится игрок
        self._client = client
        self._room = room
        # вычисляем свой id
        self.last_id += 1
        self._id = self.last_id
        # добавляем себя в комнату
        room.add_player(self)

    @property
    def id(self):
        return self._id

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return other is self

    @property
    def room(self):
        """:rtype: Room """
        return self._room

    @property
    def client(self):
        """:rtype: web.WebSocketResponse """
        return self._client

    def get_pos(self):
        return self[0:3]

    def get_rot(self):
        return self[3:5]

    def set_pos(self, x, y, z):
        self[0:3] = x, y, z
        # TODO исследовать как срабатывает __set_item__
        self.updated_state()

    def set_rot(self, a, b):
        self[3:5] = a, b
        # TODO исследовать как срабатывает __set_item__
        self.updated_state()

    def getX(self):
        return self[0]

    def getY(self):
        return self[1]

    def getZ(self):
        return self[2]

    def getA(self):
        return self[3]

    def getB(self):
        return self[4]

    def setX(self, newX):
        self[0] = newX

    def setY(self, newY):
        self[1] = newY

    def setZ(self, newZ):
        self[2] = newZ

    def setA(self, newA):
        self[3] = newA

    def setB(self, newB):
        self[4] = newB

    pos = property(get_pos, set_pos)
    rot = property(get_rot, set_rot)
    x = property(getX, setX)
    y = property(getY, setY)
    z = property(getZ, setZ)
    a = property(getA, setA)
    b = property(getB, setB)

    @property
    def as_dict(self):
        return dict(zip(('x', 'y', 'z', 'a', 'b'), self))

    @property
    def pos_as_dict(self):
        return dict(zip(('x', 'y', 'z'), self.pos))

    @property
    def rot_as_dict(self):
        return dict(zip(('a', 'b'), self.rot))

    def __setitem__(self, key, value):
        self.updated_state()

    def updated_state(self):
        # обновляем состояние (например, пересчитываем матрицу поворота)
        pass

    def append(self, p_object):
        # запрещаем добавлять элементы в наш список, не для того наследовали )
        raise NotImplementedError()


class Room(object):

    @staticmethod
    def get(_id):
        if not _id in rooms:
            rooms[_id] = Room(_id)
        return rooms[_id]

    def __init__(self, _id):
        self.id = _id
        self._players = set()

    def send_all(self, mess, except_=tuple()):
        mess = json.dumps(mess)
        for player in self._players:
            if player not in except_:
                player.client.send_str(mess)

    @property
    def players(self):
        return frozenset(self._players)

    def add_player(self, player):
        assert isinstance(player, Player)
        self._players.add(player)
        self.updated()

    def remove_player(self, player):
        assert isinstance(player, Player)
        self._players.remove(player)
        self.updated()

    def updated(self):
        # обновляем состояние (пока нечего обновлять)
        pass

# =====================================================================================================================

socket = None
clients = set()
rooms = dict()

# =====================================================================================================================


@asyncio.coroutine
def game(request):
    # room = request.match_info.get('room', "1")
    # with open('db.txt', 'r') as f:
    #     room = f.read()
    #     print ("file not empty: "+room, )
    return templ('libs.game:babylon', request, {})


@asyncio.coroutine
def test_mesh(request):
    return templ('libs.game:test_mesh', request, {})


@asyncio.coroutine
def pregame(request):
    return templ('libs.game:pregame', request, {})


@asyncio.coroutine
def check_room(request):
    found = None
    for _id, room in rooms.items():
        if len(room.players) < 3:
            print('players in room < 3:', _id)
            found = _id
            break
    else:
        while not found:
            _id = uuid4().hex[:3]
            if _id not in rooms: found = _id
    print('rroomm', found)
    return response_json(request, {"result": "ok", "room": found})


def babylon(request):
    """just draw a page of beginning of the game"""
    return templ('libs.game:game', request, {})


def h_new(me, e):
    assert not hasattr(me, 'player'), [id(me), e]

    me.player = Player(me, Room.get(e['room']), e['x'], e['y'])

    mess = dict(e="new", room=e['room'], id=me.player.id, msg='newPlayer', **me.player.as_dict)
    me.player.room.send_all(mess, except_=(me.player,))

    for player in me.player.room.players:  # // Send existing players to the new player
        if player is me.player: continue
        mess = dict(e="new", id=player.id, msg='existingPlayer', **player.as_dict)
        me.send_str(json.dumps(mess))


def h_move(me, e):
    assert hasattr(me, 'player'), [id(me), e]
    me.player.set_pos(e['x'], e['y'], e['z'])
    # print( 'e :', e )
    mess = dict(e="move", id=me.player.id, msg='move', **me.player.pos_as_dict)
    me.player.room.send_all(mess, except_=(me.player,))


def h_rotate(me, e):
    assert hasattr(me, 'player'), [id(me), e]
    me.player.set_rot(e['a'], e['b'])

    mess = dict(e="rotate", id=me.player.id, msg='rotate', **me.player.rot_as_dict)
    me.player.room.send_all(mess, except_=(me.player,))


def h_shoot(me, e):
    assert hasattr(me, 'player'), [id(me), e]
    mess = {'e':"shoot", 'id':me.player.id, 'pos':e['pos'], 'dir':e['dir'], 'd2':e['d2'], 'msg':'#{} says: pif-paf'.format(me.player.id) }
    me.player.room.send_all(mess, except_=(me.player,))


def h_chat(me, e):
    assert hasattr(me, 'player'), [id(me), e]

    mess = {'e': "chat", 'id': me.player.id, 'mes': e['mes']}
    me.player.room.send_all(mess, except_=(me.player,))


def close(me):
    assert hasattr(me, 'player'), id(me)
    print('serv onclose; id', str(me.id))

    yield from me.close()
    clean(me)


def clean(me):

    # print("clean>>>>>>>>>>>>>>",
    #           ' me:', str(me),
    #           # ' me.id:', str(me.id),
    #           ' me.player:', me.player,
    #           ' me.player.room:', me.player.room,
    #           ' me.player.id:', me.player.id
    #       )


    if hasattr(me, 'player'):
        me.player.room.remove_player(me.player)

        mess = {'e': "remove", id: me.player.id, 'msg': 'remove'}
        me.player.room.send_all(mess)
    else:
        print("onClientDisconnect   no player found", str(me.id))

    clients.remove(me)

    print('close rooms => ',   rooms   )
    print('close clients => ', clients )


def handle_game(me, e):
    e = json.loads(e)
    action = e['e']
    if action in debug_handlers:
        print('Requested action:', action)
        # print ( '======================>>>>>>>>>>>>>>>', e )
    if action in handlers:
        handler = handlers[action]
        handler(me, e)
    else:
        print('Unknown action:', e['e'], '===>>>', e)
        # send_all(e)

handlers = {
    'new': h_new,
    'move': h_move,
    'rotate': h_rotate,
    'shoot': h_shoot,
    'chat': h_chat,
}

# show all except 'move'
debug_handlers = set(handlers.keys()) - {'move'}


@asyncio.coroutine
def game_handler(request):
    # init connection
    ws = web.WebSocketResponse()
    ws.start(request)
    clients.add(ws)

    # infinite message loop
    while True:
        msg = yield from ws.receive()
        # print('yield from ', msg)
        try:
            if msg.tp == MsgType.text:
                if msg.data == 'close':
                    print('client requests close')
                    #TODO удалить из комнаты игрока если он закрыл сессию.
                    close(ws)
                else:
                    handle_game(ws, msg.data)
            elif msg.tp == aiohttp.MsgType.close:
                print('websocket connection closed')
                clean(ws)
            elif msg.tp == aiohttp.MsgType.error:
                print('ws connection closed with exception ', ws.exception())
                clean(ws)
            else:
                print('unknow websocket message type:', msg.tp, id(ws))
        except Exception as e:
            print('Dark forces tried to break down our infinite loop', e)
            traceback.print_tb(e.__traceback__)
    return ws


# def playerById(id):
#     for player in players:
#         if player.id == id:
#             return player
#     return None



    # if not os.path.exists("db.txt"):
    #     with open('db.txt', 'w', encoding='utf-8') as f:
    #         print(room, file=f)
    # if os.stat("db.txt").st_size == 0:
    #     with open('db.txt', 'w', encoding='utf-8') as f:
    #         print(room, file=f)
    # else:
    #     with open('db.txt', 'r') as f:
    #         room = f.read()
