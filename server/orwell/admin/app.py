import json

from aiohttp import web
from orwell.admin.schema import schema
from orwell.admin.schema import increase_age
from orwell.admin.schema import update_server
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
            update_server(up)
    except asyncio.CancelledError:
        pass


async def start_counter(app):
    app["counter"] = asyncio.create_task(counter(app))


async def stop_counter(app):
    app["counter"].cancel()
    await app["counter"]

app = web.Application()
app.router.add_get('/subscriptions', subscriptions)
app.router.add_get('/graphiql', graphiql_view)
app.router.add_get('/graphql', graphql_view)
app.router.add_post('/graphql', graphql_view)
app.on_startup.append(start_counter)
app.on_shutdown.append(stop_counter)
web.run_app(app, port=8000)