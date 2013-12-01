from base import BaseTest


class RegisterTestHtml(BaseTest):

    def test_page_exist(self):
        return self.page_exist('register')

    def test_user_is_created(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': '123123',
        }
        resp = self.post_with_xsrf(post_data)
        # check we are redirected to home page
        self.assert302(resp)
        self.assertEqual(resp.headers['Location'], self.reverse_url('home'))
        self.assertUserExist(self.valid_email)

    def test_password_mismatch(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': 'notequal',
        }
        resp = self.post_with_xsrf(post_data)
        # check, repsponse is not redirect
        self.assert200(resp)
        self.assertUserNotExist(self.valid_email)

    def test_bad_email(self):
        post_data = {
            'email': self.invalid_email,
            'password': '123123',
            'password2': '123123',
        }
        resp = self.post_with_xsrf(post_data)
        # check, repsponse is not redirect
        self.assert200(resp)
        self.assertUserNotExist(self.invalid_email)

    def test_duplicated_email(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': '123123',
        }
        resp = self.post_with_xsrf(post_data)
        self.assert302(resp)
        self.clear_cookie()
        # try to create user with same email
        resp = self.post_with_xsrf(post_data)
        self.assert200(resp)
        # only one user in database
        users = self.db_find('accounts', {'_id': self.valid_email})
        self.assertEqual(len(users), 1)

    def test_no_xsrf(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': '123123',
        }
        reg_url = self.reverse_url('register')
        resp = self.post(reg_url, data=post_data)
        # Forbidden
        self.assertEqual(resp.code, 403)


class RegisterTestAjax(BaseTest):

    def test_resourse_exist(self):
        resp = self.get_ajax(self.reverse_url('register'))
        self.assert200(resp)

    def test_user_is_created(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': '123123',
        }
        resp = self.post_with_xsrf(post_data, is_ajax=True)
        resp_data = self.check_json_response(resp)
        self.assertJsonSuccess(resp_data)
        self.assertUserExist(self.valid_email)
        self.assertEqual(resp_data['redirect_url'], self.reverse_url('home'))

    def test_password_mismatch(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': 'notequal',
        }
        resp = self.post_with_xsrf(post_data, is_ajax=True)
        resp_data = self.check_json_response(resp)
        self.assertJsonFail(resp_data)
        self.assertUserNotExist(self.valid_email)
        self.assertTrue('password2' in resp_data['errors'])

    def test_bad_email(self):
        post_data = {
            'email': self.invalid_email,
            'password': '123123',
            'password2': '123123',
        }
        resp = self.post_with_xsrf(post_data, is_ajax=True)
        resp_data = self.check_json_response(resp)
        self.assertJsonFail(resp_data)
        self.assertUserNotExist(self.invalid_email)
        self.assertTrue('email' in resp_data['errors'])

    def test_duplicated_email(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': '123123',
        }
        resp = self.post_with_xsrf(post_data, is_ajax=True)
        resp_data = self.check_json_response(resp)
        self.assertJsonSuccess(resp_data)
        self.clear_cookie()
        # try to create user with same email
        resp = self.post_with_xsrf(post_data, is_ajax=True)
        resp_data = self.check_json_response(resp)
        self.assertJsonFail(resp_data)
        # only one user in database
        users = self.db_find('accounts', {'_id': self.valid_email})
        self.assertEqual(len(users), 1)
        self.assertTrue('email' in resp_data['errors'])

    def test_no_xsrf(self):
        post_data = {
            'email': self.valid_email,
            'password': '123123',
            'password2': '123123',
        }
        reg_url = self.reverse_url('register')
        resp = self.post_ajax(reg_url, data=post_data)
        # Forbidden
        self.assertEqual(resp.code, 403)
