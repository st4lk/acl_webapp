#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import options
from settings import settings, MONGO_DB
from urls import url_patterns
from utils.db import connect_mongo


class ACLApp(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        db = connect_mongo(MONGO_DB, **kwargs)
        super(ACLApp, self).__init__(
            url_patterns, db=db, *args, **dict(settings, **kwargs))


def main():
    app = ACLApp()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
