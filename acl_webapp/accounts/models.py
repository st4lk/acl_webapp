from schematics.types import StringType, EmailType
from schematics.types.compound import ListType, DictType
from schematics.exceptions import ModelValidationError
from base.models import BaseModel
from .hashers import check_password, make_password


class UserModel(BaseModel):
    _id = EmailType(required=True)
    # _id = EmailType(required=True, serialized_name="email")
    password = StringType(required=True, min_length=3, max_length=50)
    permissions = DictType(ListType, compound_field=StringType)
    first_name = StringType()
    last_name = StringType()

    MONGO_COLLECTION = 'accounts'
    DEFAULT_PERMISSIONS = {"news": ['read', ]}

    @property
    def email(self):
        return self._id

    @email.setter
    def email(self, value):
        self._id = value

    @classmethod
    def process_query(cls, params):
        params = dict(params)
        if 'email' in params:
            params['_id'] = params.pop('email')
        return params

    def validate(self, *args, **kwargs):
        try:
            return super(UserModel, self).validate(*args, **kwargs)
        except ModelValidationError as e:
            if '_id' in e.message:
                e.message['email'] = e.message.pop('_id')
            raise

    def check_password(self, entered_password):
        return check_password(entered_password, self.password)

    def set_password(self, plaintext):
        self.password = make_password(plaintext)

    def get_permissions(self, model):
        model_name = model.get_model_name()
        return self.permissions.get(model_name, [])

    def has_permission(self, model, needed_permissions):
        user_permissions = set(self.get_permissions(model))
        return not (needed_permissions - user_permissions)

    def insert(self, *args, **kwargs):
        if not self.permissions:
            self.permissions = dict(self.DEFAULT_PERMISSIONS)
        return super(UserModel, self).insert(*args, **kwargs)
