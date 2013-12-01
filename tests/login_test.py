# -*- coding: utf-8 -*-
from base import BaseTest


class LoginBaseTest(BaseTest):
    @property
    def pwd(self):
        return '123456'


class LoginTest(LoginBaseTest):

    def test_page_exist(self):
        return self.page_exist('login')

    def test_login_succeeded(self):
        self.register_user(self.valid_email, self.pwd)
        self.clear_cookie()
        self.assertUserExist(self.valid_email)
        home_url = self.reverse_url('home')
        login_url = self.reverse_url('login')
        logout_url = self.reverse_url('logout')
        resp = self.get(home_url)
        # check, that user is not logged in
        self.assertTrue(login_url in resp.body)
        resp = self.post_with_xsrf(
            {'email': self.valid_email, 'password': self.pwd}, 'login')
        self.assert302(resp)
        resp = self.get(home_url)
        self.assert200(resp)
        self.assertTrue(logout_url in resp.body)

    def test_bad_email(self):
        resp = self.post_with_xsrf(
            {'email': self.invalid_email, 'password': self.pwd}, 'login')
        self.assertNotLoggedIn(resp)

    def test_wrong_password(self):
        self.register_user(self.valid_email, self.pwd)
        self.clear_cookie()
        resp = self.post_with_xsrf(
            {'email': self.valid_email, 'password': 'nott'}, 'login')
        self.assertNotLoggedIn(resp)

    def test_wrong_email(self):
        self.register_user(self.valid_email, self.pwd)
        self.clear_cookie()
        resp = self.post_with_xsrf(
            {'email': 'another@email.com', 'password': self.pwd}, 'login')
        self.assertNotLoggedIn(resp)

    def assertNotLoggedIn(self, resp):
        self.assert200(resp)
        self.assertTrue(self.reverse_url('login') in resp.body)
