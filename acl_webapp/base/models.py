import logging
from bson.objectid import ObjectId
from tornado import gen
from schematics.models import Model
from schematics.types import NumberType

logger = logging.getLogger(__name__)
MAX_FIND_LIST_LEN = 100


class BaseModel(Model):
    """
    Provides generic methods to work with model.
    Why use `MyModel.find_one` instead of `db.collection.find_one` ?
    1. Collection name is declared inside the model, so it is not needed
        to provide it all the time
    2. This `MyModel.find_one` will return MyModel instance, whereas
        `db.collection.find_one` will return dictionary

    Example with directly access:

        db_result = yield motor.Op(db.collection_name.find_one({"i": 3}))
        obj = MyModel(db_result)

    Same example, but using MyModel.find_one:

        obj = yield motor.Op(MyModel.find_one, db, {"i": 3})
    """

    _id = NumberType(number_class=ObjectId, number_type="ObjectId")

    @classmethod
    def process_params(cls, params):
        """
        Params can be modified here before actual providing to database.
        """
        return params

    @classmethod
    def get_model_name(cls):
        return cls.MONGO_COLLECTION

    @classmethod
    def get_collection(cls):
        return getattr(cls, 'MONGO_COLLECTION', None)

    @classmethod
    def check_collection(cls, collection):
        return collection or cls.get_collection()

    @classmethod
    def find_list_len(cls):
        return getattr(cls, 'FIND_LIST_LEN', MAX_FIND_LIST_LEN)

    @classmethod
    def find_one(cls, db, params, collection=None, model=True, callback=None):
        def wrap_callback(*args, **kwargs):
            result = args[0]
            error = args[1]
            if not model or error or not result:
                callback(*args, **kwargs)
            else:
                callback(cls(result), error)
        params = cls.process_params(dict(params))
        db[cls.check_collection(collection)].find_one(
            params, callback=wrap_callback)

    @classmethod
    def remove_entries(cls, db, params, collection=None, callback=None):
        c = cls.check_collection(collection)
        params = cls.process_params(dict(params))
        db[c].remove(params, callback=callback)

    def save(self, db, collection=None, ser=None, callback=None, **kwargs):
        c = self.check_collection(collection)
        data = ser or self.to_primitive()
        db[c].save(data, callback=callback, **kwargs)

    def insert(self, db, collection=None, ser=None, callback=None, **kwargs):
        c = self.check_collection(collection)
        data = ser or self.to_primitive()
        if '_id' in data and data['_id'] is None:
            del data['_id']
        db[c].insert(data, callback=callback, **kwargs)

    @gen.coroutine
    def update(self, db, collection=None, callback=None):
        # TODO
        # test it. Earlier it was used with gen.engine
        c = self.check_collection(collection)
        data = self.to_primitive()
        if '_id' not in data:
            self.save(db, c, ser=data, callback=callback)
        else:
            _id = data.pop("_id")
            (r, e), _ = yield gen.Task(db[c].update,
                {"_id": _id}, {"$set": data})
            if e or r['updatedExisting']:
                callback((r, e), _)
            else:
                data['_id'] = _id
                self.save(db, c, ser=data, callback=callback)

    @classmethod
    def find(cls, cursor, model=True, callback=None):
        def wrap_callback(*args, **kwargs):
            result = args[0]
            error = args[1]
            if not model or error or not result:
                callback(*args, **kwargs)
            else:
                for i in xrange(len(result)):
                    result[i] = cls(result[i])
                callback(result, error)
        cursor.to_list(cls.find_list_len(), callback=wrap_callback)

    @classmethod
    def get_fields(cls, role):
        rl = cls._options.roles[role]
        fields = []
        for field in cls._fields:
            if not rl(field, None):
                fields.append(field)
        return fields
