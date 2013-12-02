import logging
import json
import tornado.web
from tornado import gen
import motor
from settings import jinja_env

logger = logging.getLogger('edtr_logger')


class BaseHandler(tornado.web.RequestHandler):
    """A class to collect common handler methods - all other handlers should
    subclass this one.
    """
    def initialize(self, **kwargs):
        super(BaseHandler, self).initialize(**kwargs)
        self.db = self.settings['db']

    def render(self, template, context=None):
        """Renders template using jinja2"""
        if not context:
            context = {}
        context.update(self.get_template_namespace())
        self.write(jinja_env.get_template(template).render(context))
        # Always set _xsrf cookie
        self.xsrf_token
        self.flush()

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie('user', user)
        else:
            self.clear_cookie('user')

    @property
    def is_ajax(self):
        request_x = self.request.headers.get('X-Requested-With')
        return request_x == 'XMLHttpRequest'

    def render_json(self, data):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data))

    def get_current_user(self):
        expires = self.settings.get('cookie_expires', 31)
        return self.get_secure_cookie('user', max_age_days=expires)


class ListHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        context = yield self.get_context()
        self.render(self.template_name, context)

    @gen.coroutine
    def get_context(self):
        page = self.get_argument('page', 1)
        object_list = yield self.get_object_list(page)
        raise gen.Return({
            'object_list': object_list,
            'page': page,
        })

    def get_model(self):
        return self.model

    def get_find_filter(self):
        return {}

    def get_find_params(self):
        return {}

    @gen.coroutine
    def get_object_list(self, page=1):
        model = self.get_model()
        cursor = self.db[model.get_collection()].find(
            self.get_find_filter(), **self.get_find_params())
        if page > 1:
            cursor.skip((page-1) * model.find_list_len())
        object_list = yield motor.Op(model.find, cursor)
        raise gen.Return(object_list)
