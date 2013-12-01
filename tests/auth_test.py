from base import BaseTest


class RegisterTest(BaseTest):

    def test_page_exist(self):
        return self.page_exist('register')


class LoginTest(BaseTest):

    def test_page_exist(self):
        return self.page_exist('login')
