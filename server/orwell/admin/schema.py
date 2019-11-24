import random
import asyncio
import graphene


class Server(graphene.ObjectType):
    name = graphene.String()
    up = graphene.Boolean()
    address = graphene.String()


class ServerWrapper(object):
    def __init__(self, server):
        self._server = server
        self._queue = asyncio.Queue()

    @property
    def queue(self):
        return self._queue

    @property
    def name(self):
        return self._server.name

    @name.setter
    def name(self, value):
        if self._server.name != value:
            self._server.name = value
            self._queue.put_nowait("update")

    @property
    def up(self):
        return self._server.up

    @up.setter
    def up(self, value):
        if self._server.up != value:
            self._server.up = value
            self._queue.put_nowait("update")
            if self._server.up:
                what = "established"
            else:
                what = "lost"
            print("Connection %s with %s" % (what, self._server.name))

    @property
    def address(self):
        return self._server.address

    @address.setter
    def address(self, value):
        if self._server.address != value:
            self._server.address = value
            self._queue.put_nowait("update")


class Query(graphene.ObjectType):
    server = graphene.Field(Server)
    server_game = graphene.Field(Server)
    proxy_robots = graphene.Field(Server)
    thrower = graphene.String(required=True)
    test = graphene.String(who=graphene.String())

    def resolve_thrower(self, info):
        raise Exception("Throws!")

    def resolve_server(self, info):
        print("resolve_server(" + str(info) + ")")
        return server_game

    def resolve_server_game(self, info):
        print("resolve_server_game(" + str(info) + ")")
        return server_game

    def resolve_proxy_robots(self, info):
        print("resolve_proxy_robots(" + str(info) + ")")
        return proxy_robots

    def resolve_test(self, info, who=None):
        return 'Hello %s' % (who or 'World')


class RandomType(graphene.ObjectType):
    seconds = graphene.Int()
    random_int = graphene.Int()


computed_age = 0


def increase_age(amount):
    global computed_age
    computed_age += amount


class Subscription(graphene.ObjectType):
    count_seconds = graphene.Float(up_to=graphene.Int())
    random_int = graphene.Field(RandomType)
    age = graphene.Int()
    server_game = graphene.Field(Server)
    proxy_robots = graphene.Field(Server)

    async def resolve_count_seconds(root, info, up_to=5):
        for i in range(up_to):
            print("YIELD SECOND", i)
            yield i
            await asyncio.sleep(1.)
        yield up_to

    async def resolve_random_int(root, info):
        i = 0
        while True:
            yield RandomType(seconds=i, random_int=random.randint(0, 500))
            await asyncio.sleep(1.)
            i += 1

    async def resolve_age(root, info):
        yield computed_age

    async def resolve_server(root, info):
        while True:
            message = await server_game_wrapper.queue.get()
            if message:
                yield server_game

    async def resolve_server_game(root, info):
        while True:
            message = await server_game_wrapper.queue.get()
            if message:
                yield server_game

    async def resolve_proxy_robots(root, info):
        while True:
            message = await proxy_robots_wrapper.queue.get()
            if message:
                yield proxy_robots


schema = graphene.Schema(query=Query, subscription=Subscription)

server_game = Server(name="ServerGame", up=False, address="")

server_game_wrapper = ServerWrapper(server_game)

proxy_robots = Server(name="ProxyRobots", up=False, address="")

proxy_robots_wrapper = ServerWrapper(proxy_robots)

server_queue = asyncio.Queue()
