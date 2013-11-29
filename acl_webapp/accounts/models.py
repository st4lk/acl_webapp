from schematics.types import StringType, EmailType
from schematics.exceptions import ModelValidationError
from base.models import BaseModel
from .hashers import check_password, make_password


class UserModel(BaseModel):
    _id = EmailType(required=True)
    password = StringType(required=True, min_length=6, max_length=50)
    first_name = StringType()
    last_name = StringType()

    MONGO_COLLECTION = 'accounts'

    @property
    def email(self):
        return self._id

    @email.setter
    def email(self, value):
        self._id = value

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