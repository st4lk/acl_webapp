# -*- coding: utf-8 -*-
from base import BaseTest


class LogoutTest(BaseTest):

    def test_logout(self):
        home_url = self.reverse_url('home')
        logout_url = self.reverse_url('logout')
        self.register_user('vasya@vasya.com', 'qweqweqwe')
        resp = self.get(home_url)
        self.assertTrue(logout_url in resp.body)
        resp = self.get(logout_url)
        self.assertEqual(resp.code, 302)
        self.assertEqual(resp.headers['Location'], home_url)
        resp = self.get(home_url)
        self.assertFalse(logout_url in resp.body)
