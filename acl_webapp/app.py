#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import options
import motor
from settings import settings, mongo_address, MONGO_DB
from urls import url_patterns


class ACLApp(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        mongo_addr = kwargs.get('mongo_addr', mongo_address)
        mongo_db = kwargs.get('mongo_db', MONGO_DB)
        db = motor.MotorClient(**mongo_addr).open_sync()[mongo_db]
        super(ACLApp, self).__init__(
            url_patterns, db=db, *args, **dict(settings, **kwargs))


def main():
    app = ACLApp()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
