# -*- coding: utf-8 -*-
import logging
from tornado import gen
import motor

from base.handlers import ListHandler
from .models import NewsModel

l = logging.getLogger(__name__)


class NewsListHandler(ListHandler):

    def initialize(self, **kwargs):
        super(NewsListHandler, self).initialize(**kwargs)
        self.model = NewsModel
        self.template_name = "news/list.html"
