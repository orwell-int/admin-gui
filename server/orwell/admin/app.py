import json
import sys

from aiohttp import web
import asyncio
import zmq
import zmq.asyncio

from graphql import format_error
from graphql_ws.aiohttp import AiohttpSubscriptionServer

from orwell_common.broadcast import AsyncBroadcast
from orwell_common.broadcast import ServerGameDecoder
from orwell_common.broadcast import ProxyRobotsDecoder

from orwell.admin.schema import schema
from orwell.admin.schema import increase_age
from orwell.admin.schema import server_game_wrapper as server_game
from orwell.admin.schema import proxy_robots_wrapper as proxy_robots
from orwell.admin.template import render_graphiql


async def graphql_view(request):
    payload = await request.json()
    response = await schema.execute(payload.get('query', ''), return_promise=True)
    data = {}
    if response.errors:
        data['errors'] = [format_error(e) for e in response.errors]
    if response.data:
        data['data'] = response.data
    jsondata = json.dumps(data,)
    return web.Response(text=jsondata, headers={'Content-Type': 'application/json'})


async def graphiql_view(request):
    return web.Response(text=render_graphiql(), headers={'Content-Type': 'text/html'})

subscription_server = AiohttpSubscriptionServer(schema)


async def subscriptions(request):
    ws = web.WebSocketResponse(protocols=('graphql-ws',))
    await ws.prepare(request)

    await subscription_server.handle(ws)
    return ws


async def counter(app):
    try:
        up = False
        while True:
            await asyncio.sleep(5)
            up = not up
            increase_age(1)
    except asyncio.CancelledError:
        pass


zmq_server_game_queue = asyncio.Queue()
zmq_proxy_robots_queue = asyncio.Queue()


async def broadcast_server_game(app):
    try:
        broadcast = AsyncBroadcast(ServerGameDecoder())
        while True:
            if not server_game.up:
                await broadcast.async_send_all_broadcast_messages()
                if broadcast.decoder.success:
                    server_game.up = True
                    server_game.address = broadcast.remote_address
                    await zmq_server_game_queue.put(broadcast.decoder.agent_address)
            await asyncio.sleep(2.1)
    except asyncio.CancelledError:
        pass


async def broadcast_proxy_robots(app):
    try:
        broadcast = AsyncBroadcast(
            ProxyRobotsDecoder(version="admin"), port=9081)
        while True:
            if not proxy_robots.up:
                await broadcast.async_send_all_broadcast_messages()
                if broadcast.decoder.success:
                    proxy_robots.up = True
                    proxy_robots.address = broadcast.remote_address
                    await zmq_proxy_robots_queue.put(
                        "tcp://{address}:{port}".format(
                            address=proxy_robots.address,
                            port=broadcast.decoder.port))
            await asyncio.sleep(2.1)
    except asyncio.CancelledError:
        pass


async def get_server_game_info(app):
    try:
        zmq_req_socket = None
        while True:
            idle = True
            if server_game.up:
                try:
                    try:
                        agent_address = zmq_server_game_queue.get_nowait()
                        if agent_address:
                            zmq_req_socket = zmq.asyncio.Socket(
                                app["context"], zmq.REQ)
                            zmq_req_socket.setsockopt(zmq.LINGER, 1)
                            print("ServerGame zmq connect to %s", agent_address)
                            zmq_req_socket.connect(agent_address)
                    except asyncio.QueueEmpty as ex:
                        print(ex, file=sys.stderr)
                    if zmq_req_socket:
                        for item in ("robot", "player"):
                            print("ServerGame zmq send 'list %s'" % item)
                            await zmq_req_socket.send_string("list %s" % item)
                            response = await asyncio.wait_for(
                                zmq_req_socket.recv_unicode(), 1)
                            print("ServerGame zmq received: ", response)
                except zmq.ZMQError as zex:
                    print("ServerGame ZMQ error: ", zex, file=sys.stderr)
                    server_game.up = False
                except asyncio.TimeoutError as tex:
                    print("ServerGame Timeout while trying "
                          "to receive ZMQ response. ",
                          tex, file=sys.stderr)
                    server_game.up = False
            if idle:
                await asyncio.sleep(2.2)
    except asyncio.CancelledError:
        pass


async def get_proxy_robots_info(app):
    try:
        zmq_req_socket = None
        while True:
            idle = True
            if proxy_robots.up:
                try:
                    try:
                        agent_address = zmq_proxy_robots_queue.get_nowait()
                        if agent_address:
                            zmq_req_socket = zmq.asyncio.Socket(
                                app["context"], zmq.REQ)
                            zmq_req_socket.setsockopt(zmq.LINGER, 1)
                            print("ProxyRobots zmq connect to %s", agent_address)
                            zmq_req_socket.connect(agent_address)
                    except asyncio.QueueEmpty as ex:
                        print(ex, file=sys.stderr)
                    if zmq_req_socket:
                        for item in ("robot",):
                            print("ProxyRobots zmq send 'list %s'" % item)
                            await zmq_req_socket.send_string("list %s" % item)
                            response = await asyncio.wait_for(
                                zmq_req_socket.recv_unicode(), 1)
                            print("ProxyRobots zmq received: ", response)
                except zmq.ZMQError as zex:
                    print("ProxyRobots ZMQ error: ", zex, file=sys.stderr)
                    proxy_robots.up = False
                except asyncio.TimeoutError as tex:
                    print("ProxyRobots Timeout while trying "
                          "to receive ZMQ response. ",
                          tex, file=sys.stderr)
                    proxy_robots.up = False
            if idle:
                await asyncio.sleep(2.2)
    except asyncio.CancelledError:
        pass

APP_NAMES = "names"
APP_CONTEXT = "context"


def add_task(app, function, name):
    app[name] = asyncio.create_task(function(app))
    app[APP_NAMES].append(name)


async def start_callbacks(app):
    app[APP_NAMES] = []
    app[APP_CONTEXT] = zmq.asyncio.Context()
    add_task(app, counter, "counter")
    add_task(app, broadcast_server_game, "broadcast_server_game")
    add_task(app, broadcast_proxy_robots, "broadcast_proxy_robots")
    add_task(app, get_server_game_info, "get_server_game_info")
    add_task(app, get_proxy_robots_info, "get_proxy_robots_info")


async def stop_callbacks(app):
    for name in app[APP_NAMES]:
        app[name].cancel()
    for name in app[APP_NAMES]:
        await app[name]


print("Route /subscriptions")
print("Route /graphiql")
print("Route /graphql")
app = web.Application()
app.router.add_get('/subscriptions', subscriptions)
app.router.add_get('/graphiql', graphiql_view)
app.router.add_get('/graphql', graphql_view)
app.router.add_post('/graphql', graphql_view)
app.on_startup.append(start_callbacks)
app.on_shutdown.append(stop_callbacks)
web.run_app(app, port=8000)