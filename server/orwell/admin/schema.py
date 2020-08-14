import random
import asyncio
import graphene

import collections


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


class Arguments(object):
    def __init__(
            self,
            cls,
            interfaces=(),
            possible_types=(),
            default_resolver=None,
            _meta=None,
            **options
    ):
        self.stored_cls = cls
        self.stored_interfaces = interfaces
        self.stored_possible_types = possible_types
        self.stored_default_resolver = default_resolver
        self.stored_meta = _meta
        self.stored_options = options


global_arguments = {}


class ObjectTypeDelayed(graphene.ObjectType):
    """
    Ugly way of simulating resolveThunk to avoid circular dependencies.

    You need to implement as static method named get_delayed_fields to
    return a dictionary with the additional fields needed.

      @staticmethod
      def get_delayed_fields():
          return {}

    You need to call call_delayed_init in the class to initialize everything.

    WARNING:
      This is highly experimental. It seems to work but there might be
      unsuspected side effects of delaying the initialisation.
    """
    @classmethod
    def __init_subclass_with_meta__(
            cls,
            interfaces=(),
            possible_types=(),
            default_resolver=None,
            _meta=None,
            **options
    ):
        arguments = Arguments(
            cls,
            interfaces,
            possible_types,
            default_resolver,
            _meta,
            **options)
        global_arguments[cls.__name__] = arguments

    # code copied from graphene/types/objecttype.py
    @classmethod
    def __init_subclass_with_meta_delayed__(
            cls,
            interfaces=(),
            possible_types=(),
            default_resolver=None,
            _meta=None,
            additional_fields=None,
            **options
    ):
        print("__init_subclass_with_meta__(cls=" + str(cls)
              + ", interfaces=" + str(interfaces)
              + ", possible_types=" + str(possible_types)
              + ",...)")
        if not _meta:
            _meta = graphene.types.objecttype.ObjectTypeOptions(cls)

        fields = collections.OrderedDict()

        for interface in interfaces:
            assert issubclass(interface, graphene.Interface), (
                'All interfaces of {} must be a subclass of Interface.'
                ' Received "{}".'
            ).format(cls.__name__, interface)
            fields.update(interface._meta.fields)

        for base in reversed(cls.__mro__):
            fields.update(graphene.types.utils.yank_fields_from_attrs(
                base.__dict__, _as=graphene.Field))

        print("__init_subclass_with_meta__ ; "
              "fields=[" + ", ".join([str(f) for f in fields]) + "]")
        assert not (possible_types and cls.is_type_of), (
            "{name}.Meta.possible_types will cause type collision with "
            "{name}.is_type_of. Please use one or other."
        ).format(name=cls.__name__)

        if additional_fields:
            fields.update(additional_fields)

        if _meta.fields:
            _meta.fields.update(fields)
        else:
            _meta.fields = fields

        if not _meta.interfaces:
            _meta.interfaces = interfaces
        _meta.possible_types = possible_types
        _meta.default_resolver = default_resolver

        super(graphene.ObjectType, cls).__init_subclass_with_meta__(
            _meta=_meta, **options)

    @classmethod
    def call_delayed_init(cls):
        args = global_arguments[cls.__name__]
        delayed_fields = cls.get_delayed_fields()
        cls.__init_subclass_with_meta_delayed__(
            args.stored_interfaces,
            args.stored_possible_types,
            args.stored_default_resolver,
            args.stored_meta,
            delayed_fields,
            **args.stored_options)


class Robot(ObjectTypeDelayed):
    name = graphene.String()
    registered = graphene.Boolean()
    video_url = graphene.String()
    # (Robot <--> Player)

    @staticmethod
    def get_delayed_fields():
        return {"player": graphene.Field(Player)}


class RobotWrapper(object):
    def __init__(self, robot, queue=None):
        self._robot = robot
        if queue:
            self._queue = queue
        else:
            self._queue = asyncio.Queue()

    @property
    def queue(self):
        return self._queue

    @property
    def name(self):
        return self._robot.name

    @name.setter
    def name(self, value):
        if self._robot.name != value:
            self._robot.name = value
            self._queue.put_nowait("update:" + self.name)

    @property
    def registered(self):
        return self._robot.registered

    @registered.setter
    def registered(self, value):
        if self._robot.registered != value:
            self._robot.registered = value
            self._queue.put_nowait("update:" + self.name)
            if self._robot.registered:
                what = "registered"
            else:
                what = "unregistered"
            print("Robot %s is now %s" % (what, self._robot.name))

    @property
    def video_url(self):
        return self._robot.video_url

    @video_url.setter
    def video_url(self, value):
        if self._robot.video_url != value:
            self._robot.video_url = value
            self._queue.put_nowait("update:" + self.name)

    @property
    def player(self):
        return self._robot.player

    @player.setter
    def player(self, value):
        player = None
        if isinstance(value, str):
            if value in players:
                player = players[value]
        elif isinstance(value, Player):
            player = value
        if player:
            if self._robot.player != player:
                self._robot.player = player
                player.robot = self.name
            self._queue.put_nowait("update:" + self.name)
        else:
            print(" !! invalid player", player)

    def get(self):
        return self._robot


class Player(graphene.ObjectType):
    name = graphene.String()
    address = graphene.String()
    robot = graphene.Field(Robot)


Robot.call_delayed_init()


class PlayerWrapper(object):
    def __init__(self, player, queue=None):
        self._player = player
        if queue:
            self._queue = queue
        else:
            self._queue = asyncio.Queue()

    @property
    def queue(self):
        return self._queue

    @property
    def name(self):
        return self._player.name

    @name.setter
    def name(self, value):
        if self._player.name != value:
            self._player.name = value
            self._queue.put_nowait("update:" + self.name)

    @property
    def address(self):
        return self._player.address

    @address.setter
    def address(self, value):
        if self._player.address != value:
            self._player.address = value
            self._queue.put_nowait("update:" + self.address)

    @property
    def robot(self):
        return self._player.robot

    @robot.setter
    def robot(self, value):
        robot = None
        if isinstance(value, str):
            if value in robots:
                robot = robots[value]
        elif isinstance(value, Player):
            robot = value
        if robot:
            if self._player.robot != robot:
                self._player.robot = robot
                robot.player = self.name
            self._queue.put_nowait("update:" + self.name)
        else:
            print(" !! invalid robot", robot)

    def get(self):
        return self._player


class Team(graphene.ObjectType):
    name = graphene.String()
    score = graphene.Int()
    robots = graphene.List(graphene.NonNull(Robot))


class TeamWrapper(object):
    def __init__(self, team, queue=None):
        self._team = team
        if self._team.robots is None:
            # This is a part that is still a bit obscure
            # (putting the array of robots directly in the GraphQL object)
            self._team.robots = []
        if queue:
            self._queue = queue
        else:
            self._queue = asyncio.Queue()

    @property
    def queue(self):
        return self._queue

    @property
    def name(self):
        return self._team.name

    @name.setter
    def name(self, value):
        if self._team.name != value:
            self._team.name = value
            self._queue.put_nowait("update:" + self.name)

    def get(self):
        return self._team

    @property
    def score(self):
        return self._team.score

    @score.setter
    def score(self, value):
        if self._team.score != value:
            self._team.score = value
            self._queue.put_nowait("update:" + self.name)

    @property
    def robots(self):
        return self._team.robots

    @robots.setter
    def robots(self, new_robots):
        print("Set robots from:", new_robots)
        print("self._team.robots =", self._team.robots)
        add_robots = []
        for new_robot in new_robots:
            robot = None
            if isinstance(new_robot, str):
                print("Try to add robot with name ", new_robot)
                if new_robot in robots:
                    robot = robots[new_robot]
                    print("Robot found:", robot)
                else:
                    print("Robot NOT found")
            if robot is not None:
                if robot not in self._team.robots:
                    add_robots.append(robot)
        remove_robots = []
        for old_robot in self._team.robots:
            print("  look for robot:", old_robot.name)
            found = False
            for new_robot in new_robots:
                print("    check against robot:", new_robot)
                if old_robot.name == new_robot:
                    found = True
                    break
            if not found:
                remove_robots.append(old_robot)
            else:
                print("keep robot:", old_robot.name)
        for remove_robot in remove_robots:
            print("remove robot:", remove_robot.name)
            self._team.robots.remove(remove_robot)
        for add_robot in add_robots:
            print("add robot:", add_robot.name)
            self._team.robots.append(add_robot)
        if remove_robots or add_robots:
            self._queue.put_nowait("update:" + self.name)


class Items(object):
    def __init__(self):
        self._queue = asyncio.Queue()
        self._items = {}

    @property
    def queue(self):
        return self._queue

    def add(self, item):
        updated = False
        if isinstance(item, Robot):
            if item.name not in self._items:
                self._items[item.name] = RobotWrapper(item, self._queue)
                print("Added a Robot")
                updated = True
        elif isinstance(item, Player):
            if item.name not in self._items:
                self._items[item.name] = PlayerWrapper(item, self._queue)
                print("Added a Player")
                updated = True
        elif isinstance(item, Team):
            if item.name not in self._items:
                self._items[item.name] = TeamWrapper(item, self._queue)
                print("Added a Team")
                updated = True
        else:
            raise TypeError(
                "item should be either of type Robot or Player or Team")
        if updated:
            print("+ queue.put:", item)
            self._queue.put_nowait("add:" + item.name)

    def clear(self):
        if self._items:
            self._items.clear()
            self._queue.put_nowait("delete:")

    def __setitem__(self, name, item):
        if name != item.name:
            raise ValueError(
                "The name '%s' of the item does not match "
                "the given name '%s'".format(item.name, name))
        self._items[name] = item
        self._queue.put_nowait("update:" + item.name)

    def __getitem__(self, name):
        item = self._items[name]
        return item

    def __len__(self):
        return len(self._item)

    def __delitem__(self, name):
        item = self._items[name]
        del self._items[name]
        self._queue.put_nowait("delete:" + name)
        if isinstance(item, RobotWrapper):
            print("Removed a RobotWrapper")
        elif isinstance(item, PlayerWrapper):
            print("Removed a PlayerWrapper")
        elif isinstance(item, TeamWrapper):
            print("Removed a TeamWrapper")
        else:
            raise TypeError(
                "item should be either of type Robot or Player or Team")

    def keys(self):
        return self._items.keys()

    def has_key(self, name):
        return name in self._items

    def values(self):
        return [item.get() for item in self._items.values()]

#    def items(self):
#        return self._items.items()

    def __contains__(self, item):
        return item in self._items

#    def __iter__(self):
#        return iter(self._items)


class Game(graphene.ObjectType):
    time = graphene.Int()
    running = graphene.Boolean()
    duration = graphene.Int()


class GameWrapper(object):
    def __init__(self, game, queue=None):
        self._game = game
        if queue:
            self._queue = queue
        else:
            self._queue = asyncio.Queue()

    def get(self):
        return self._game

    @property
    def queue(self):
        return self._queue

    @property
    def time(self):
        return self._game.time

    @time.setter
    def time(self, value):
        if self._game.time != value:
            self._game.time = value
            self._queue.put_nowait("update:time")

    @property
    def running(self):
        return self._game.running

    @running.setter
    def running(self, value):
        if self._game.running != value:
            self._game.running = value
            self._queue.put_nowait("update:running")

    @property
    def duration(self):
        return self._game.duration

    @duration.setter
    def duration(self, value):
        if self._game.duration != value:
            self._game.duration = value
            self._queue.put_nowait("update:duration")


class Query(graphene.ObjectType):
    server = graphene.Field(Server)
    server_game = graphene.Field(Server)
    proxy_robots = graphene.Field(Server)
    robots = graphene.List(graphene.NonNull(Robot))
    players = graphene.List(graphene.NonNull(Player))
    teams = graphene.List(graphene.NonNull(Team))
    robot = graphene.Field(Robot, name=graphene.String(required=True))
    player = graphene.Field(Player, name=graphene.String(required=True))
    team = graphene.Field(Team, name=graphene.String(required=True))
    game = graphene.Field(Game)
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

    def resolve_robots(self, info):
        print("resolve_robots(" + str(info) + ")")
        return robots.values()

    def resolve_players(self, info):
        print("resolve_players(" + str(info) + ")")
        return players.values()

    def resolve_teams(self, info):
        print("resolve_teams(" + str(info) + ")")
        return teams.values()

    def resolve_robot(self, info, name):
        print("resolve_robot(" + str(info) + ")")
        if name in robots:
            # returning the wrapper or the raw object seem to work
            return robots[name]
        else:
            return None

    def resolve_player(self, info, name):
        print("resolve_player(" + str(info) + ")")
        if name in players:
            # returning the wrapper or the raw object seem to work
            return players[name]
        else:
            return None

    def resolve_team(self, info, name):
        print("resolve_team(" + str(info) + ")")
        if name in teams:
            # returning the wrapper or the raw object seem to work
            return teams[name]
        else:
            return None

    def resolve_game(self, info):
        print("resolve_game(" + str(info) + ")")
        return global_game

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
    robots = graphene.List(graphene.NonNull(Robot))
    players = graphene.List(graphene.NonNull(Player))
    teams = graphene.List(graphene.NonNull(Team))
    robot = graphene.Field(Robot, name=graphene.String(required=True))
    player = graphene.Field(Player, name=graphene.String(required=True))
    team = graphene.Field(Team, name=graphene.String(required=True))
    game = graphene.Field(Game)

    async def resolve_count_seconds(self, info, up_to=5):
        for i in range(up_to):
            print("YIELD SECOND", i)
            yield i
            await asyncio.sleep(1.)
        yield up_to

    async def resolve_random_int(self, info):
        i = 0
        while True:
            yield RandomType(seconds=i, random_int=random.randint(0, 500))
            await asyncio.sleep(1.)
            i += 1

    async def resolve_age(self, info):
        yield computed_age

    async def resolve_server(self, info):
        print("Subscription::resolve_server(" + str(info) + ")")
        while True:
            message = await server_game_wrapper.queue.get()
            if message:
                yield server_game

    async def resolve_server_game(self, info):
        print("Subscription::resolve_server_game(" + str(info) + ")")
        while True:
            message = await server_game_wrapper.queue.get()
            if message:
                yield server_game

    async def resolve_proxy_robots(self, info):
        print("Subscription::resolve_proxy_robots(" + str(info) + ")")
        while True:
            message = await proxy_robots_wrapper.queue.get()
            if message:
                yield proxy_robots

    async def resolve_robots(self, info):
        print("Subscription::resolve_robots(" + str(info) + ")")
        while True:
            message = await robots.queue.get()
            if message:
                if ':' in message:
                    command, _, argument = message.partition(':')
                    if command in ("add", "update", "delete"):
                        yield robots.values()

    async def resolve_players(self, info):
        print("Subscription::resolve_players(" + str(info) + ")")
        while True:
            message = await players.queue.get()
            if message:
                if ':' in message:
                    command, _, argument = message.partition(':')
                    if command in ("add", "update", "delete"):
                        yield players.values()

    async def resolve_teams(self, info):
        print("Subscription::resolve_teams(" + str(info) + ")")
        while True:
            message = await teams.queue.get()
            if message:
                if ':' in message:
                    command, _, argument = message.partition(':')
                    if command in ("add", "update", "delete"):
                        yield teams.values()

    async def resolve_robot(self, info, name):
        print("Subscription::resolve_robot(" + str(info) + ", " + repr(name) + ")")
        while True:
            message = await robots.queue.get()
            if message:
                if ':' in message:
                    command, _, argument = message.partition(':')
                    if command in ("add", "update", "delete"):
                        if name == argument:
                            yield robots[name].get()

    async def resolve_player(self, info, name):
        print("Subscription::resolve_player(" + str(info) + ", " + repr(name) + ")")
        while True:
            message = await players.queue.get()
            if message:
                if ':' in message:
                    command, _, argument = message.partition(':')
                    if command in ("add", "update", "delete"):
                        if name == argument:
                            yield players[name].get()

    async def resolve_team(self, info, name):
        print("Subscription::resolve_team(" + str(info) + ", " + repr(name) + ")")
        while True:
            message = await teams.queue.get()
            if message:
                if ':' in message:
                    command, _, argument = message.partition(':')
                    if command in ("add", "update", "delete"):
                        if name == argument:
                            yield teams[name].get()

    async def resolve_game(self, info):
        while True:
            message = await global_game_wrapper.queue.get()
            if message:
                if ':' in message:
                    command, _, argument = message.partition(':')
                    if command in ("add", "update", "delete"):
                        yield global_game


schema = graphene.Schema(query=Query, subscription=Subscription)

server_game = Server(name="ServerGame", up=False, address="")

server_game_wrapper = ServerWrapper(server_game)

proxy_robots = Server(name="ProxyRobots", up=False, address="")

proxy_robots_wrapper = ServerWrapper(proxy_robots)

# robot name -> robot
robots = Items()

# player name -> player
players = Items()

# team name -> team
teams = Items()

global_game = Game()

global_game_wrapper = GameWrapper(global_game)

server_queue = asyncio.Queue()
