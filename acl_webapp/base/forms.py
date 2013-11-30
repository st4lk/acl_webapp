# -*- coding: utf-8 -*-
import logging
from wtforms_tornado import Form
from schematics.exceptions import ValidationError as ModelValidationError

l = logging.getLogger(__name__)


class ModelNotProvidedException(Exception):
    pass


class ModelForm(Form):
    """
    Form, that is linked to model.
    Example:

    class MyMorm(ModelForm):
        email = StringField('Email Address', [validators.InputRequired()])

        _model = MyModel # required

    _model must contain model class

    In addition to Form validation, performs validation from model.
    If validation passes, model object can be accessed by `get_object` method.
    """
    # TODO
    # create form fields from provided model dynamically.
    # Not to duplicate the code, i.e. repeating fields in model and in from.

    # TODO
    # find a way to perform validation, that depends on database access
    # currently, if function is wrapped with @gen.coroutine, exception
    # is ignored

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self._model_object = None

    def get_object(self):
        return self._model_object

    def get_model(self):
        model = getattr(self, '_model', None)
        if model is None:
            raise ModelNotProvidedException()
        return model

    def set_field_error(self, field_name, err_msg):
        getattr(self, field_name).errors.append(err_msg)

    def validate(self):
        valid = super(ModelForm, self).validate()
        model = self.get_model()
        obj = model()
        self.populate_obj(obj)
        try:
            obj.validate()
        except ModelValidationError as e:
            if isinstance(e.message, dict):
                for field_name, err_msgs in e.message.items():
                    errors = getattr(self, field_name).errors
                    if not errors:
                        errors.extend(err_msgs)
            else:
                l.warning("Unknown validation error: '{0}'".format(e))
                if self._errors is None:
                    self._errors = {}
                self._errors['whole_form'] = ["Unknown error.", ]
            return False
        self._model_object = obj
        return valid
