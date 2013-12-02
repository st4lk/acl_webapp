# -*- coding: utf-8 -*-
import re
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


class RegisterError(Exception):
    pass


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

    def post_with_xsrf(self, data=None, url_name='register', url=None,
            is_ajax=False):
        url = url or self.reverse_url(url_name)
        resp = self.get(url)
        # add xsrf to post request
        data['_xsrf'] = re.search(
            '<input type="hidden" name="_xsrf" value="(.*?)"', resp.body)\
            .group(1)
        if is_ajax:
            return self.post_ajax(url, data=data)
        else:
            return self.post(url, data=data)

    def register_user(self, email, password):
        data = {
            'email': email,
            'password': password,
            'password2': password,
        }
        resp = self.post_with_xsrf(data)
        if resp.code != 302:
            raise RegisterError()
        return resp

    def db_clear(self):
        @gen.engine
        def async_op():
            yield motor.Op(db.accounts.remove)
            yield motor.Op(db.news.remove)
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

    def assertJsonSuccess(self, json_data):
        self.assertTrue(json_data['result'])

    def assertJsonFail(self, json_data):
        self.assertFalse(json_data['result'])

    def assertUserExist(self, email):
        user = self.db_find_one('accounts', {'_id': email})
        self.assertEqual(user['_id'], email)

    def assertUserNotExist(self, email):
        user = self.db_find_one('accounts', {'_id': email})
        self.assertEqual(user, None)

    def assert302(self, resp):
        self.assertEqual(resp.code, 302)

    def assert403(self, resp):
        self.assertEqual(resp.code, 403)

    def assert200(self, resp):
        self.assertEqual(resp.code, 200)

    def assertUserLoggedIn(self, resp=None):
        if resp is None:
            resp = self.get(self.reverse_url('home'))
        self.assert200(resp)
        self.assertTrue(self.reverse_url('logout') in resp.body)

    def assertNotLoggedIn(self, resp=None):
        if resp is None:
            resp = self.get(self.reverse_url('home'))
        self.assert200(resp)
        self.assertTrue(self.reverse_url('login') in resp.body)

    @property
    def valid_email(self):
        return 'vasya@vasya.com'

    @property
    def invalid_email(self):
        return 'bad_email'
