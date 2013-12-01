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
        resp = self.get(home_url)
        self.assertNotLoggedIn(resp)
        resp = self.post_with_xsrf(
            {'email': self.valid_email, 'password': self.pwd}, 'login')
        self.assert302(resp)
        self.assertUserLoggedIn()

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


class LoginAjaxTest(LoginBaseTest):

    def test_resourse_exist(self):
        resp = self.get_ajax(self.reverse_url('login'))
        self.assert200(resp)

    def test_login_succeeded(self):
        self.register_user(self.valid_email, self.pwd)
        self.clear_cookie()
        self.assertUserExist(self.valid_email)
        home_url = self.reverse_url('home')
        resp = self.get(home_url)
        self.assertNotLoggedIn(resp)
        resp = self.post_with_xsrf(url_name='login', is_ajax=True,
            data={'email': self.valid_email, 'password': self.pwd})
        resp_data = self.check_json_response(resp)
        self.assertJsonSuccess(resp_data)
        self.assertUserLoggedIn()

    def test_bad_email(self):
        resp = self.post_with_xsrf(url_name='login', is_ajax=True,
            data={'email': self.invalid_email, 'password': self.pwd})
        resp_data = self.check_json_response(resp)
        self.assertJsonFail(resp_data)
        self.assertTrue('email' in resp_data['errors'])
        self.assertNotLoggedIn()

    def test_wrong_password(self):
        self.register_user(self.valid_email, self.pwd)
        self.clear_cookie()
        resp = self.post_with_xsrf(url_name='login', is_ajax=True,
            data={'email': self.valid_email, 'password': 'nott'})
        resp_data = self.check_json_response(resp)
        self.assertJsonFail(resp_data)
        self.assertTrue('password' in resp_data['errors'])
        self.assertNotLoggedIn()

    def test_wrong_email(self):
        self.register_user(self.valid_email, self.pwd)
        self.clear_cookie()
        resp = self.post_with_xsrf(url_name='login', is_ajax=True,
            data={'email': 'another@email.com', 'password': self.pwd})
        resp_data = self.check_json_response(resp)
        self.assertJsonFail(resp_data)
        self.assertTrue('email' in resp_data['errors'])
        self.assertNotLoggedIn()
