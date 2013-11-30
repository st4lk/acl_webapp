import logging
from collections import defaultdict
from pymongo.errors import DuplicateKeyError
from tornado import gen
import motor

from base.handlers import BaseHandler
from .forms import RegistrationForm

l = logging.getLogger(__name__)


class RegisterHandler(BaseHandler):
    """Handler for registration page. Show and process register form.
    """
    def initialize(self, **kwargs):
        super(RegisterHandler, self).initialize(**kwargs)
        self.template_name = "accounts/register.html"
        self.context = {'errors': defaultdict(list), }

    def get(self):
        form = RegistrationForm()
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
                form.set_field_error('email', "Already taken. Sorry.")
            else:
                # user save succeeded
                self.set_current_user(usr.email)
                self.redirect(self.reverse_url("home"))
                return
        self.render(self.template_name, {"form": form})


class LogoutHandler(BaseHandler):
    """Handler for logout url. Delete session and redirect to home page.
    """

    def get(self):
        self.set_current_user(None)
        self.redirect(self.reverse_url("home"))
