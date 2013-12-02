import logging
import json
from functools import wraps
import tornado.web
from tornado import gen
import motor
from settings import jinja_env

logger = logging.getLogger('edtr_logger')


def check_skip_permissions(func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        if self.skip_permissions:
            return True
        return func(self, *args, **kwargs)
    return wrapped


class PermissionMixin(object):

    @check_skip_permissions
    def check_permission(self, user):
        if not user:
            return False
        return user.has_permission(self.model, self.needed_permissions)

    def get_permission_denied_template(self):
        template_name = getattr(self, 'permission_denied_template', None)
        if template_name is None:
            template_name = "permission_denied.html"
        return template_name

    def get_permission_denied_context(self):
        return {}

    def render_permission_denied(self):
        context = self.get_permission_denied_context()
        template_name = self.get_permission_denied_template()
        self.render(template_name, context)


class BaseHandler(tornado.web.RequestHandler, PermissionMixin):
    """A class to collect common handler methods - all other handlers should
    subclass this one.
    """
    def initialize(self, **kwargs):
        super(BaseHandler, self).initialize(**kwargs)
        self.db = self.settings['db']
        self.skip_permissions = True

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

    @gen.coroutine
    def get_current_user_object(self):
        from accounts.models import UserModel
        email = self.current_user
        if email:
            # TODO cache
            user = yield motor.Op(
                UserModel.find_one, self.db, {"email": email})
        else:
            user = None
        raise gen.Return(user)


class ListHandler(BaseHandler):

    def initialize(self, **kwargs):
        super(ListHandler, self).initialize(**kwargs)
        self.skip_permissions = False
        self.needed_permissions = set(['read'])

    @gen.coroutine
    def get(self):
        user = yield self.get_current_user_object()
        if self.check_permission(user):
            context = yield self.get_context()
            self.render(self.template_name, context)
        else:
            self.render_permission_denied()

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
