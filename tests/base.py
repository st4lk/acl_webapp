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

    def page_exist(self, url_name):
        url = self.reverse_url(url_name)
        self.http_client.fetch(self.get_url(url), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
