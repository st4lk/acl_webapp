import logging
from collections import defaultdict
from pymongo.errors import DuplicateKeyError
from tornado import gen
import motor
from schematics.exceptions import ValidationError

from base.handlers import BaseHandler
from .models import UserModel

l = logging.getLogger(__name__)


class RegisterHandler(BaseHandler):
    """Handler for registration page. Show and process register form.
    """
    def initialize(self, **kwargs):
        super(RegisterHandler, self).initialize(**kwargs)
        self.template_name = "accounts/register.html"
        self.context = {'errors': defaultdict(list), }

    def get(self):
        self.render(self.template_name, self.context)

    @gen.coroutine
    def post(self):
        password = self.get_argument('password1', None)
        password2 = self.get_argument('password2', None)

        if password != password2:
            self.context['errors']['password2'].append("Passwords not equal")
            self.render(self.template_name, self.context)
            return

        usr = UserModel()
        usr.email = self.get_argument("email", None)
        usr.password = password

        valid = True
        try:
            usr.validate()
        except ValidationError as e:
            valid = False
            if isinstance(e.message, dict):
                for field_name, err_msgs in e.message.items():
                    self.context['errors'][field_name].extend(err_msgs)
            else:
                l.warning("Unknown validation error: '{0}'".format(e))
                self.context['non-field'] = "Unknown error."

        if valid:
            usr.set_password(usr.password)
            try:
                yield motor.Op(usr.save, self.db)
                # user save succeeded
                self.set_current_user(usr.email)
                self.redirect(self.reverse_url("home"))
                return
            except DuplicateKeyError:
                self.context['errors']['email']. \
                    append("Already taken. Sorry.")

        l.debug(self.context)
        self.render(self.template_name, self.context)


class LogoutHandler(BaseHandler):
    """Handler for logout url. Delete session and redirect to home page.
    """

    def get(self):
        self.set_current_user(None)
        self.redirect(self.reverse_url("home"))
