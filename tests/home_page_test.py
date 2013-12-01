# -*- coding: utf-8 -*-
from base import BaseTest


class HomePageTest(BaseTest):

    def test_page_exist(self):
        url = self.reverse_url('home')
        self.http_client.fetch(self.get_url(url), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
