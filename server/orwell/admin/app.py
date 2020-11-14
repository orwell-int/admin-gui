import json
import sys
import traceback
import logging

from aiohttp import web
import asyncio
import zmq
import zmq.asyncio

from graphql import format_error
from graphql_ws.aiohttp import AiohttpSubscriptionServer

from orwell_common.broadcast import AsyncBroadcast
from orwell_common.broadcast import ServerGameDecoder
from orwell_common.broadcast import ProxyRobotsDecoder
import orwell_common.logging

from orwell.admin.schema import schema
from orwell.admin.schema import increase_age
from orwell.admin.schema import server_game_wrapper as server_game
from orwell.admin.schema import proxy_robots_wrapper as proxy_robots
from orwell.admin.schema import Robot
from orwell.admin.schema import Player
from orwell.admin.schema import Team
from orwell.admin.schema import robots
from orwell.admin.schema import players
from orwell.admin.schema import teams
from orwell.admin.schema import global_game_wrapper as global_game
from orwell.admin.template import render_graphiql

proxy_robots_robots = None

LOGGER = logging.getLogger("orwell")


async def graphql_view(request):
    payload = await request.json()
    response = await schema.execute(payload.get('query', ''), return_promise=True)
    data = {}
    if response.errors:
        data['errors'] = [format_error(e) for e in response.errors]
    if response.data:
        data['data'] = response.data
    jsondata = json.dumps(data, )
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


def decode_game(json_message):
    global_game.time = json_message["time"]
    global_game.running = json_message["running"]
    global_game.duration = json_message["duration"]


def update_items(items, new_items):
    to_remove = []
    for key in items.keys():
        if key in new_items:
            value = new_items[key]
            items.add(value)
            new_items.pop(key)
        else:
            to_remove.append(key)
    for key, value in new_items.items():
        items.add(value)
    for key in to_remove:
        del items[key]


def decode_robots(json_message):
    mappings = {}
    new_robots = {}
    for json_robot in json_message["Robots"]:
        robot = Robot()
        if "id" in json_robot:
            robot.id = json_robot["id"]
            if proxy_robots_robots and robot.id in proxy_robots_robots:
                robot.address = proxy_robots_robots[robot.id]["address"]
        robot.name = json_robot["name"]
        robot.registered = json_robot["registered"]
        robot.video_url = json_robot["video_url"]
        robot.description = "Tank"  # HARDCODED
        new_robots[robot.name] = robot
        mappings[robot.name] = json_robot["player"]
    update_items(robots, new_robots)
    return mappings


def decode_players(json_message):
    mappings = {}
    new_players = {}
    for json_player in json_message["Players"]:
        player = Player()
        player.name = json_player["name"]
        if "address" in json_player:
            player.address = json_player["address"]
        new_players[player.name] = player
        if "robot" in json_player:
            robot_name = json_player["robot"]
            if robot_name:
                # only if the player has a robot
                mappings[player.name] = robot_name
    update_items(players, new_players)
    return mappings


def decode_teams(json_message):
    new_teams = {}
    for team_name in json_message["Teams"]:
        team = Team()
        team.name = team_name
        new_teams[team.name] = team
    update_items(teams, new_teams)


def decode_team(json_message, team):
    json_team = json_message["Team"]
    if team.name != json_team["name"]:
        print("Wrong team name (" + json_team["name"]
              + ") expected " + team.name)
        return
    team.score = json_team["score"]
    team.robots = json_team["robots"]


def clean_server_game():
    server_game.up = False
    robots.clear()
    players.clear()
    teams.clear()


def clean_proxy_robots():
    proxy_robots.up = False
    global proxy_robots_robots
    proxy_robots_robots = None
    for robot in robots.values():
        robot.address = ""


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
                        print("ServerGame zmq send 'json get game'")
                        await zmq_req_socket.send_string("json get game")
                        response = await asyncio.wait_for(
                            zmq_req_socket.recv_unicode(), 1)
                        print("ServerGame zmq received: ", response)
                        json_response = json.loads(response)
                        decode_game(json_response)

                        robot_to_player = {}
                        player_to_robot = {}
                        for item in ("robot", "player", "team"):
                            print("ServerGame zmq send 'json list %s'" % item)
                            await zmq_req_socket.send_string("json list %s" % item)
                            response = await asyncio.wait_for(
                                zmq_req_socket.recv_unicode(), 1)
                            print("ServerGame zmq received: ", response)
                            json_response = json.loads(response)
                            if "robot" == item:
                                robot_to_player.update(decode_robots(json_response))
                            elif "player" == item:
                                decoded = decode_players(json_response)
                                if decoded:
                                    player_to_robot.update(decoded)
                            elif "team" == item:
                                decode_teams(json_response)
                        for player_name, robot_name in player_to_robot.items():
                            if player_name != robot_to_player[robot_name]:
                                print("Corrupted links!", robot_name, player_name)
                                print("robot_to_player =", robot_to_player)
                                print("player_to_robot =", player_to_robot)
                                continue
                            robots[robot_name].player = player_name
                        for team_name in teams.keys():
                            team = teams[team_name]
                            print("team_name =", team_name, "; team =", team)
                            command = "json view team " + team_name
                            print("ServerGame zmq send '" + command + "'")
                            await zmq_req_socket.send_string(command)
                            response = await asyncio.wait_for(
                                zmq_req_socket.recv_unicode(), 1)
                            print("zmq response: " + response)
                            json_response = json.loads(response)
                            decode_team(json_response, team)
                except zmq.ZMQError as zex:
                    print("ServerGame ZMQ error: ", zex, file=sys.stderr)
                    clean_server_game()
                except asyncio.TimeoutError as tex:
                    print("ServerGame Timeout while trying "
                          "to receive ZMQ response. ",
                          tex, file=sys.stderr)
                    clean_server_game()
            if idle:
                await asyncio.sleep(2.2)
    except asyncio.CancelledError:
        pass


async def raw_get_proxy_robots_info(app):
    global proxy_robots_robots
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
                            print("ProxyRobots zmq connect to ", agent_address)
                            zmq_req_socket.connect(agent_address)
                    except asyncio.QueueEmpty as ex:
                        print(ex, file=sys.stderr)
                    if zmq_req_socket:
                        for item in ("robot",):
                            command = "json list %s" % item
                            LOGGER.info("ProxyRobots zmq send '%s'", command)
                            await zmq_req_socket.send_string(command)
                            response = await asyncio.wait_for(
                                zmq_req_socket.recv_unicode(), 1)
                            LOGGER.info("ProxyRobots zmq received: %s", response)
                            robots_dict = json.loads(response)
                            LOGGER.debug("robots: %s", robots)
                            for robot in robots.values():
                                if robot.id and robot.id in robots_dict:
                                    json_robot = robots_dict[robot.id]
                                    robot.address = json_robot["address"]
                            proxy_robots_robots = robots_dict
                except zmq.ZMQError as zex:
                    print("ProxyRobots ZMQ error: ", zex, file=sys.stderr)
                    clean_proxy_robots()
                except asyncio.TimeoutError as tex:
                    LOGGER.error(
                        "ProxyRobots Timeout while trying "
                        "to receive ZMQ response. %s",
                        tex)
                    traceback.print_exc()
                    clean_proxy_robots()
            if idle:
                await asyncio.sleep(2.2)
    except asyncio.CancelledError:
        pass


async def get_proxy_robots_info(app):
    try:
        await raw_get_proxy_robots_info(app)
    except Exception as uex:
        print("Unexpected exception in get_proxy_robots_info")
        traceback.print_exc()
        raise uex


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


def main():
    print("Route /subscriptions")
    print("Route /graphiql")
    print("Route /graphql")
    orwell_common.logging.configure_logging(False)
    app = web.Application()
    app.router.add_get('/subscriptions', subscriptions)
    app.router.add_get('/graphiql', graphiql_view)
    app.router.add_get('/graphql', graphql_view)
    app.router.add_post('/graphql', graphql_view)
    app.on_startup.append(start_callbacks)
    app.on_shutdown.append(stop_callbacks)
    web.run_app(app, port=8000)


if '__main__' == __name__:
    main()
