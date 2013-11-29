import logging
from tornado import gen
from base.handlers import BaseHandler

l = logging.getLogger(__name__)


class HomeHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        self.render("home.html")
