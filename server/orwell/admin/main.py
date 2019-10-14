from typing import Optional, Awaitable

import tornado
import tornado.ioloop
import tornado.web

from graphene_tornado.tornado_graphql_handler import TornadoGraphQLHandler

import orwell.admin.model as model

import datetime

from orwell.admin.model import schema


import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class MainHandler(tornado.web.RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def get(self):
        self.write("Orwell administration interface")


class Application(tornado.web.Application):
    def __init__(self, handlers):
        handlers += [
            (r'/graphql', TornadoGraphQLHandler, dict(graphiql=True, schema=schema)),
        ]
        tornado.web.Application.__init__(self, handlers)


def make_app():
    return Application([
        (r"/", MainHandler),
    ])


def timeout_function():
    model.server.up = not model.server.up
    tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=5), timeout_function)


def main():
    web_port = 8888
    app = make_app()
    app.listen(web_port)
    print("Webserver will be available on port", web_port)
    server = model.Server()
    server.name = "GameServer"
    server.up = False
    #print(schema.introspect().items())
    tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=5), timeout_function)
    tornado.ioloop.IOLoop.current().start()


if "__main__" == __name__:
    main()
