from typing import Optional, Awaitable

import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def get(self):
        self.write("Orwell administration interface")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


def main():
    web_port = 8888
    app = make_app()
    app.listen(web_port)
    print("Webserver will be available on port", web_port)
    tornado.ioloop.IOLoop.current().start()


if "__main__" == __name__:
    main()
