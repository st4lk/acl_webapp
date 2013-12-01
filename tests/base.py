# -*- coding: utf-8 -*-
import Cookie
import json
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase
from tornado.ioloop import IOLoop
from tornado import gen
import motor
from app import ACLApp
from acl_webapp.base.models import MAX_FIND_LIST_LEN
from libs.http_test_client import TestClient


MONGO_TEST_DB = 'acl_app_test'
app = ACLApp(mongo_db=MONGO_TEST_DB)
reverse_url = app.reverse_url
db = app.settings['db']


class BaseTest(AsyncHTTPTestCase, LogTrapTestCase, TestClient):

    def setUp(self):
        super(BaseTest, self).setUp()
        self.reverse_url = reverse_url
        self.cookies = Cookie.SimpleCookie()
        ### clear data base before each test
        self.db_clear()

    def get_app(self):
        return app

    def page_exist(self, url_name):
        url = self.reverse_url(url_name)
        resp = self.get(url)
        self.assertEqual(resp.code, 200)

    def get_new_ioloop(self):
        return IOLoop.instance()

    def check_json_response(self, response):
        self.assertEqual(response.code, 200)
        json_resp = json.loads(response.body)
        return json_resp

    def db_clear(self):
        @gen.engine
        def async_op():
            yield motor.Op(db.accounts.remove)
            self.stop()
        async_op()
        self.wait()

    def db_find_one(self, collection, data):
        @gen.engine
        def async_op():
            result = yield motor.Op(db[collection].find_one, data)
            self.stop(result)
        async_op()
        return self.wait()

    def db_find(self, collection, data):
        @gen.engine
        def async_op(cursor):
            result = yield motor.Op(cursor.to_list, MAX_FIND_LIST_LEN)
            self.stop(result)
        cursor = db[collection].find(data)
        async_op(cursor)
        return self.wait()

    def db_save(self, collection, data):
        @gen.engine
        def async_op():
            result = yield motor.Op(db[collection].save, data)
            self.stop(result)
        async_op()
        return self.wait()
