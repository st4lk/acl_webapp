import logging
from handlers.base import BaseHandler

l = logging.getLogger(__name__)


class HomeHandler(BaseHandler):

    def get(self):
        self.render("home.html")
