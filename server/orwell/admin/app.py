import json
import sys

from aiohttp import web
from orwell.admin.schema import schema
from orwell.admin.schema import increase_age
from orwell.admin.schema import update_server
from orwell.admin.schema import is_server_up
from graphql import format_error
from graphql_ws.aiohttp import AiohttpSubscriptionServer
import asyncio

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
            #update_server(up)
    except asyncio.CancelledError:
        pass


from orwell_common.broadcast import AsyncBroadcast
from orwell_common.broadcast import ServerGameDecoder
import zmq
import zmq.asyncio

zmq_queue = asyncio.Queue()


async def broadcast_server_game(app):
    try:
        broadcast = AsyncBroadcast(ServerGameDecoder())
        while True:
            if not is_server_up():
                await broadcast.async_send_all_broadcast_messages()
                if broadcast.decoder.success:
                    update_server(True)
                    await zmq_queue.put(broadcast.decoder.agent_address)
            await asyncio.sleep(2.1)
    except asyncio.CancelledError:
        pass


async def get_server_info(app):
    try:
        zmq_req_socket = None
        while True:
            idle = True
            if is_server_up():
                try:
                    try:
                        agent_address = zmq_queue.get_nowait()
                        if agent_address:
                            zmq_req_socket = zmq.asyncio.Socket(
                                app["context"], zmq.REQ)
                            zmq_req_socket.setsockopt(zmq.LINGER, 1)
                            print("zmq connect to %s", agent_address)
                            zmq_req_socket.connect(agent_address)
                    except asyncio.QueueEmpty as ex:
                        print(ex, file=sys.stderr)
                    if zmq_req_socket:
                        for item in ("robot", "player"):
                            print("zmq send 'list %s'" % item)
                            await zmq_req_socket.send_string("list %s" % item)
                            response = await zmq_req_socket.recv_unicode()
                            print("zmq received: ", response)
                except zmq.ZMQError as zex:
                    print(zex, file=sys.stderr)
                    update_server(False)
            if idle:
                await asyncio.sleep(2.2)
    except asyncio.CancelledError:
        pass


def add_task(app, function, name):
    app[name] = asyncio.create_task(function(app))
    app["names"].append(name)


async def start_counter(app):
    app["names"] = []
    app["context"] = zmq.asyncio.Context()
    add_task(app, counter, "counter")
    add_task(app, broadcast_server_game, "broadcast_server_game")
    add_task(app, get_server_info, "get_server_info")


async def stop_counter(app):
    for name in app["names"]:
        app[name].cancel()
    for name in app["names"]:
        await app[name]


print("Route /subscriptions")
print("Route /graphiql")
print("Route /graphql")
app = web.Application()
app.router.add_get('/subscriptions', subscriptions)
app.router.add_get('/graphiql', graphiql_view)
app.router.add_get('/graphql', graphql_view)
app.router.add_post('/graphql', graphql_view)
app.on_startup.append(start_counter)
app.on_shutdown.append(stop_counter)
web.run_app(app, port=8000)