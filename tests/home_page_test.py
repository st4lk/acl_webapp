# -*- coding: utf-8 -*-
from base import BaseTest


class HomePageTest(BaseTest):

    def test_page_exist(self):
        return self.page_exist('home')
