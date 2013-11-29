import logging
from tornado import gen
# import tornado.web
import motor
from handlers.base import BaseHandler

l = logging.getLogger(__name__)


class HomeHandler(BaseHandler):

    # @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        obj = yield motor.Op(self.db.test_collection.find_one, {'i': 3})
        self.render("home.html", {'obj': obj})
