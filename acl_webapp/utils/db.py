import motor
import time
import logging
from pymongo.errors import ConnectionFailure
from tornado.ioloop import IOLoop

l = logging.getLogger(__name__)


def get_db():
    return getattr(IOLoop.current(), 'app_instance').settings['db']


def get_bc_db():
    return getattr(IOLoop.current(), 'app_instance').settings['bc_db']


def connect_mongo(mongo_settings, **kwargs):
    mongo_addr = kwargs.get('mongo_addr',
        {'host': mongo_settings['host'], 'port': mongo_settings['port']})
    mongo_db = kwargs.get('mongo_db', mongo_settings['db_name'])
    db = None
    for i in xrange(mongo_settings['reconnect_tries'] + 1):
        try:
            db = motor.MotorClient(**mongo_addr).open_sync()[mongo_db]
        except ConnectionFailure:
            if i >= mongo_settings['reconnect_tries']:
                raise
            else:
                timeout = mongo_settings['reconnect_timeout']
                l.warning("ConnectionFailure #{0} during server start, "
                    "waiting {1} seconds"
                    .format(i+1, timeout))
                time.sleep(timeout)
        else:
            break
    return db
