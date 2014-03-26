import logging
from datetime import timedelta
from bson.objectid import ObjectId
from tornado import gen, ioloop
import motor
from schematics.models import Model
from schematics.types import NumberType
from pymongo.errors import ConnectionFailure
from settings import MONGO_DB

l = logging.getLogger(__name__)
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

        obj = yield MyModel.find_one(db, {"i": 3})
    """

    _id = NumberType(number_class=ObjectId, number_type="ObjectId")

    def __init__(self, *args, **kwargs):
        self.set_db(kwargs.pop('db', None))
        super(BaseModel, self).__init__(*args, **kwargs)

    @property
    def db(self):
        return getattr(self, '_db', None)

    def set_db(self, db):
        self._db = db

    @classmethod
    def process_query(cls, query):
        """
        query can be modified here before actual providing to database.
        """
        return dict(query)

    @property
    def pk(self):
        return self._id

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
    @gen.coroutine
    def find_one(cls, db, query, collection=None, model=True):
        result = None
        query = cls.process_query(query)
        for i in cls.reconnect_amount():
            try:
                result = yield motor.Op(
                    db[cls.check_collection(collection)].find_one, query)
            except ConnectionFailure as e:
                exceed = yield cls.check_reconnect_tries_and_wait(i,
                    'find_one')
                if exceed:
                    raise e
            else:
                if model and result:
                    result = cls.make_model(result, "find_one", db=db)
                raise gen.Return(result)

    @classmethod
    def remove_entries(cls, db, params, collection=None, callback=None):
        c = cls.check_collection(collection)
        params = cls.process_query(params)
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

    @classmethod
    @gen.coroutine
    def aggregate(cls, db, pipe_list, collection=None):
        c = cls.check_collection(collection)
        for i in cls.reconnect_amount():
            try:
                result = yield motor.Op(db[c].aggregate, pipe_list)
            except ConnectionFailure as e:
                exceed = yield cls.check_reconnect_tries_and_wait(i,
                    'aggregate')
                if exceed:
                    raise e
            else:
                raise gen.Return(result)

    @staticmethod
    def reconnect_amount():
        return xrange(MONGO_DB['reconnect_tries'] + 1)

    @classmethod
    @gen.coroutine
    def check_reconnect_tries_and_wait(cls, reconnect_number, func_name):
        if reconnect_number >= MONGO_DB['reconnect_tries']:
            raise gen.Return(True)
        else:
            timeout = MONGO_DB['reconnect_timeout']
            l.warning("ConnectionFailure #{0} in {1}.{2}. Waiting {3} seconds"
                .format(
                    reconnect_number + 1, cls.__name__, func_name, timeout))
            io_loop = ioloop.IOLoop.instance()
            yield gen.Task(io_loop.add_timeout, timedelta(seconds=timeout))

    def get_data_for_save(self, ser):
        data = ser or self.to_primitive()
        if '_id' in data and data['_id'] is None:
            del data['_id']
        return data

    @classmethod
    def make_model(cls, data, method_name, field_names_set=None, db=None):
        """
        Create model instance from data (dict).
        """
        if field_names_set is None:
            field_names_set = set(cls._fields.keys())
        else:
            if not isinstance(field_names_set, set):
                field_names_set = set(field_names_set)
        new_keys = set(data.keys()) - field_names_set
        if new_keys:
            l.warning(
                "'{0}' has unhandled fields in DB: "
                "'{1}'. {2} returned data: '{3}'"
                .format(cls.__name__, new_keys, data, method_name))
            for new_key in new_keys:
                del data[new_key]
        return cls(raw_data=data, db=db)
