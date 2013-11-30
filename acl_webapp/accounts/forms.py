# -*- coding: utf-8 -*-
import logging
from base.forms import ModelForm, Form
from wtforms import StringField, PasswordField, validators
from wtforms.validators import ValidationError
from .models import UserModel

l = logging.getLogger(__name__)


class RegistrationForm(ModelForm):
    email = StringField('Email Address', [validators.InputRequired()])
    password = PasswordField('Password', [validators.InputRequired()])
    password2 = PasswordField('Repeat password', [validators.InputRequired()])

    _model = UserModel
    text_errors = {
        "password_mismatch": "Password mismatch",
        "email_occupied": "Already taken. Sorry.",
    }

    def validate_password2(self, field):
        if self.password.data != field.data:
            raise ValidationError(self.text_errors['password_mismatch'])


class LoginForm(Form):
    email = StringField('Email Address', [validators.InputRequired()])
    password = PasswordField('Password', [validators.InputRequired()])

    text_errors = {
        'not_found': "Email and password mismatch",
        'wrong_password': "Email and password mismatch",
    }
