# -*- coding: utf-8 -*-
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase
from app import ACLApp


MONGO_TEST_DB = 'acl_app_test'
app = ACLApp(mongo_db=MONGO_TEST_DB)
reverse_url = app.reverse_url


class BaseTest(AsyncHTTPTestCase, LogTrapTestCase):

    def setUp(self):
        super(BaseTest, self).setUp()
        self.reverse_url = reverse_url

    def get_app(self):
        return app
