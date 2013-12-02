# -*- coding: utf-8 -*-
from base import BaseTest


class NewsBaseTest(BaseTest):

    @property
    def valid_title(self):
        return 'news_title'

    @property
    def valid_content(self):
        return 'news content'

    def get_simple_news_data(self, title=None, content=None, author=None):
        title = title or self.valid_title
        content = content or self.valid_content
        author = author or 'author@no.net'
        return {'title': title, 'content': content, 'author': author}

    def create_news(self, title=None, content=None, author=None):
        self.db_save('news',
            self.get_simple_news_data(title, content, author))

    def set_user_permissions(self, email, permissions):
        usr = self.db_find_one('accounts', {"_id": email})
        usr['permissions']['news'] = permissions
        self.db_save('accounts', usr)


class NewsListTest(NewsBaseTest):

    def test_page_exist(self):
        return self.page_exist('news_list')

    def test_user_not_logged_in(self):
        self.create_news()
        resp = self.get(self.reverse_url('news_list'))
        self.assert200(resp)
        self.assertTrue(self.valid_title not in resp.body)

    def test_user_no_permissions(self):
        self.create_news()
        self.register_user(self.valid_email, '123123')
        self.set_user_permissions(self.valid_email, [])
        resp = self.get(self.reverse_url('news_list'))
        self.assert200(resp)
        self.assertTrue(self.valid_title not in resp.body)
        self.assertTrue(self.reverse_url('news_create') not in resp.body)

    def test_user_has_default_read_permissions(self):
        self.create_news()
        self.register_user(self.valid_email, '123123')
        resp = self.get(self.reverse_url('news_list'))
        self.assert200(resp)
        self.assertTrue(self.valid_title in resp.body)
        self.assertTrue(self.reverse_url('news_create') not in resp.body)

    def test_user_has_read_write_permissions(self):
        self.create_news()
        self.register_user(self.valid_email, '123123')
        self.set_user_permissions(self.valid_email, ['read', 'write'])
        resp = self.get(self.reverse_url('news_list'))
        self.assert200(resp)
        self.assertTrue(self.valid_title in resp.body)
        self.assertTrue(self.reverse_url('news_create') in resp.body)


class NewsCreateTest(NewsBaseTest):
    def test_user_not_logged_in(self):
        resp = self.get(self.reverse_url('news_create'))
        self.assert302(resp)
        self.assertTrue(self.reverse_url('login') in resp.headers['Location'])

    def test_user_default_no_permissions(self):
        self.register_user(self.valid_email, '123123')
        resp = self.get(self.reverse_url('news_create'))
        self.assert200(resp)
        self.assertTrue('Publish' not in resp.body)

    def test_user_has_write_permissions(self):
        self.register_user(self.valid_email, '123123')
        self.set_user_permissions(self.valid_email, ['read', 'write'])
        resp = self.get(self.reverse_url('news_create'))
        self.assert200(resp)
        self.assertTrue('Publish' in resp.body)

    def test_post_is_saved(self):
        self.register_user(self.valid_email, '123123')
        self.set_user_permissions(self.valid_email, ['read', 'write'])
        resp = self.post_with_xsrf(
            data=self.get_simple_news_data(),
            url_name="news_create"
        )
        self.assert302(resp)
        self.assertEqual(resp.headers['Location'],
            self.reverse_url('news_list'))
        news = self.db_find_one('news', {"title": self.valid_title})
        self.assertTrue(news is not None)
        resp = self.get(self.reverse_url('news_list'))
        self.assertTrue(self.valid_title in resp.body)
