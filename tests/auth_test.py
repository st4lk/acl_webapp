import re
from base import BaseTest


class RegisterTest(BaseTest):

    def test_page_exist(self):
        return self.page_exist('register')

    def test_user_is_created(self):
        email = 'vasya@vasya.com'
        post_data = {
            'email': email,
            'password': '123123',
            'password2': '123123',
        }
        reg_url = self.reverse_url('register')
        resp = self.get(reg_url)
        # add xsrf to post request
        post_data['_xsrf'] = re.search(
            '<input type="hidden" name="_xsrf" value="(.*?)"', resp.body)\
            .group(1)
        resp = self.post(reg_url, data=post_data)
        # check we are redirected to home page
        self.assertEqual(resp.code, 302)
        self.assertEqual(resp.headers['Location'], self.reverse_url('home'))
        # check, user is created
        user = self.db_find_one('accounts', {'_id': email})
        self.assertEqual(user['_id'], email)


class LoginTest(BaseTest):

    def test_page_exist(self):
        return self.page_exist('login')
