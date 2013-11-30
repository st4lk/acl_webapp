# -*- coding: utf-8 -*-
import logging
from base.forms import ModelForm
from wtforms import StringField, PasswordField, validators
from wtforms.validators import ValidationError
from .models import UserModel

l = logging.getLogger(__name__)


class RegistrationForm(ModelForm):
    email = StringField('Email Address', [validators.InputRequired()])
    password = PasswordField('Password', [validators.InputRequired()])
    password2 = PasswordField('Repeat password', [validators.InputRequired()])

    _model = UserModel

    def validate_password2(self, field):
        if self.password.data != field.data:
            raise ValidationError("Password mismatch")
