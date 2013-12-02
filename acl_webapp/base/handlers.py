import logging
import json
from bson.objectid import ObjectId
import tornado.web
from tornado import gen
import motor
from pymongo.errors import DuplicateKeyError
from settings import jinja_env
from .decorators import check_skip_permissions

logger = logging.getLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):
    """A class to collect common handler methods - all other handlers should
    subclass this one.
    """
    def initialize(self, **kwargs):
        super(BaseHandler, self).initialize(**kwargs)
        self.db = self.settings['db']
        self.current_user_object = None
        self.template_name = None

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

    def get_login_url(self):
        return self.reverse_url('login')

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
        self.current_user_object = user
        raise gen.Return(user)

    def add_additional_context(self, context):
        context.update({})


class PermissionBaseHandler(BaseHandler):

    def initialize(self, **kwargs):
        super(PermissionBaseHandler, self).initialize(**kwargs)
        self.skip_permissions = True
        self.user_permissions = []

    @gen.coroutine
    def get(self, *args, **kwargs):
        permitted = yield self.user_is_permitted()
        if permitted:
            context = yield self.get_context()
            self.render(self.template_name, context)
        else:
            self.render_permission_denied()

    def add_context_permissions(self, context):
        context.update({'permissions': self.user_permissions})
        return context

    @check_skip_permissions
    def check_permission(self, user, needed_permissions=None):
        needed_permissions = needed_permissions or self.needed_permissions
        if not user:
            return False
        return user.has_permission(self.get_model(), needed_permissions)

    def set_user_permissions(self, user):
        self.user_permissions = user.get_permissions(self.get_model())

    @gen.coroutine
    def user_is_permitted(self):
        user = self.current_user_object
        if user is None:
            user = yield self.get_current_user_object()
        result = self.check_permission(user)
        if result:
            self.set_user_permissions(user)
        raise gen.Return(self.check_permission(user))

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


class ListHandler(PermissionBaseHandler):

    def initialize(self, **kwargs):
        super(ListHandler, self).initialize(**kwargs)
        self.skip_permissions = False
        self.needed_permissions = set(['read'])

    @gen.coroutine
    def get_context(self):
        page = self.get_argument('page', 1)
        object_list = yield self.get_object_list(page)
        context = {
            'object_list': object_list,
            'page': page,
        }
        self.add_context_permissions(context)
        self.add_additional_context(context)
        raise gen.Return(context)

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


class CreateHandler(PermissionBaseHandler):
    def initialize(self, **kwargs):
        super(CreateHandler, self).initialize(**kwargs)
        self.skip_permissions = False
        self.needed_permissions = set(['write'])
        self.model = None
        self.form_class = False
        self.success_url = None

    @gen.coroutine
    def post(self, *args, **kwargs):
        permitted = yield self.user_is_permitted()
        if permitted:
            form = self.post_form()
            if form.validate():
                result = yield self.form_valid(form)
                if result:
                    self.post_success()
                    return
            self.form_invalid(form)
        else:
            self.render_permission_denied()

    @gen.coroutine
    def form_valid(self, form):
        obj = form.get_object()
        result = False
        try:
            yield motor.Op(obj.insert, self.db)
            result = True
        except DuplicateKeyError:
            form.set_nonfield_error("duplicate_error")
        raise gen.Return(result)

    def form_invalid(self, form):
        context = {'form': form}
        self.add_context_permissions(context)
        self.add_additional_context(context)
        self.render(self.template_name, context)

    def post_success(self):
        self.redirect(self.get_success_url())

    def get_model(self):
        if self.model:
            return self.model
        model_class = self.get_form_class()
        return getattr(model_class, '_model', None)

    def get_form_class(self):
        return self.form_class

    def get_form_kwargs(self):
        return {}

    def get_form(self):
        return self.get_form_class()(**self.get_form_kwargs())

    def post_form(self):
        return self.get_form_class()(
            self.request.arguments, **self.get_form_kwargs())

    def get_success_url(self):
        return self.success_url

    @gen.coroutine
    def get_context(self):
        context = {
            'form': self.get_form(),
        }
        self.add_context_permissions(context)
        self.add_additional_context(context)
        raise gen.Return(context)


class DetailHandler(PermissionBaseHandler):
    def initialize(self, **kwargs):
        super(DetailHandler, self).initialize(**kwargs)
        self.skip_permissions = False
        self.needed_permissions = set(['read'])
        self.model = None

    def get_model(self):
        return self.model

    @gen.coroutine
    def get_object(self):
        model = self.get_model()
        obj_id = ObjectId(self.path_kwargs['object_id'])
        obj = yield motor.Op(model.find_one, self.db, {"_id": obj_id})
        raise gen.Return(obj)

    @gen.coroutine
    def get_context(self):
        obj = yield self.get_object()
        context = {
            'obj': obj,
        }
        self.add_context_permissions(context)
        self.add_additional_context(context)
        raise gen.Return(context)
