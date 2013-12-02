# -*- coding: utf-8 -*-
import logging
from base.forms import ModelForm
from wtforms import StringField, TextAreaField, validators
from .models import NewsModel

l = logging.getLogger(__name__)


class NewsForm(ModelForm):
    title = StringField("Title", [validators.InputRequired()])
    content = TextAreaField("Content", [validators.InputRequired()])

    _model = NewsModel
