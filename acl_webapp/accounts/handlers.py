import logging
from pymongo.errors import DuplicateKeyError
from tornado import gen
import motor

from base.handlers import BaseHandler
from .forms import RegistrationForm, LoginForm
from .models import UserModel

l = logging.getLogger(__name__)


class AuthMixin(object):

    def authenticate(self, user):
        self.set_current_user(user.email)
        self.redirect(self.reverse_url("home"))


class RegisterHandler(BaseHandler, AuthMixin):
    """Handler for registration page. Show and process register form.
    """
    def initialize(self, **kwargs):
        super(RegisterHandler, self).initialize(**kwargs)
        self.template_name = "accounts/register.html"
        self.template_name_ajax = "accounts/register_ajax.html"

    def get(self):
        form = RegistrationForm()
        if self.is_ajax():
            self.render(self.template_name_ajax, {'form': form})
        else:
            self.render(self.template_name, {'form': form})

    @gen.coroutine
    def post(self):
        form = RegistrationForm(self.request.arguments)
        if form.validate():
            usr = form.get_object()
            usr.set_password(usr.password)
            try:
                yield motor.Op(usr.insert, self.db)
            except DuplicateKeyError:
                form.set_field_error('email', 'email_occupied')
            else:
                # user save succeeded
                self.authenticate(usr)
                return
        self.render(self.template_name, {"form": form})


class LogoutHandler(BaseHandler):
    """Handler for logout url. Delete session and redirect to home page.
    """

    def get(self):
        self.set_current_user(None)
        self.redirect(self.reverse_url("home"))


class LoginHandler(BaseHandler, AuthMixin):
    """Handler for login page. Show and process login form.
    """
    def initialize(self, **kwargs):
        super(LoginHandler, self).initialize(**kwargs)
        self.template_name = "accounts/login.html"

    def get(self):
        form = LoginForm()
        self.render(self.template_name, {"form": form})

    @gen.coroutine
    def post(self):
        form = LoginForm(self.request.arguments)
        if form.validate():
            usr = yield motor.Op(UserModel.find_one, self.db, {
                "email": form.email.data})
            if usr:
                if usr.check_password(form.password.data):
                    self.authenticate(usr)
                    return
                else:
                    form.set_field_error('password', 'wrong_password')
            else:
                form.set_field_error('email', 'not_found')
        self.render(self.template_name, {"form": form})
