# -*- coding: utf-8 -*-
import logging
from tornado import gen
from tornado import web
import motor
from base.handlers import ListHandler, CreateHandler, DetailHandler,\
    DeleteHandler
from .models import NewsModel
from .forms import NewsForm

l = logging.getLogger(__name__)


class NewsListHandler(ListHandler):

    def initialize(self, **kwargs):
        super(NewsListHandler, self).initialize(**kwargs)
        self.model = NewsModel
        self.template_name = "news/list.html"


class NewsCreateHandler(CreateHandler):
    def initialize(self, **kwargs):
        super(NewsCreateHandler, self).initialize(**kwargs)
        self.template_name = "news/create.html"
        self.form_class = NewsForm
        self.success_url = self.reverse_url('news_list')

    @web.authenticated
    @gen.coroutine
    def get(self, *args, **kwargs):
        yield super(NewsCreateHandler, self).get(*args, **kwargs)

    @web.authenticated
    @gen.coroutine
    def post(self, *args, **kwargs):
        yield super(NewsCreateHandler, self).post(*args, **kwargs)

    @gen.coroutine
    def form_valid(self, form):
        obj = form.get_object()
        obj.author = self.current_user
        yield motor.Op(obj.insert, self.db)
        raise gen.Return(True)


class NewsDetailHandler(DetailHandler):
    def initialize(self, **kwargs):
        super(NewsDetailHandler, self).initialize(**kwargs)
        self.template_name = "news/detail.html"
        self.model = NewsModel


class NewsDeleteHandler(DeleteHandler):
    def initialize(self, **kwargs):
        super(NewsDeleteHandler, self).initialize(**kwargs)
        self.template_name = "news/delete.html"
        self.model = NewsModel
        self.success_url = self.reverse_url('news_list')

    @gen.coroutine
    def get_additional_permissions(self):
        if self.object is None:
            yield self.get_object()
        news = self.object
        raise gen.Return(news.author == self.current_user)

    def render_permission_denied(self):
        raise web.HTTPError(403, "Permission denied")
