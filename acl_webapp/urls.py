from tornado.web import url

from pages.handlers import HomeHandler


url_patterns = [
    url(r"/", HomeHandler, name="home"),
]
