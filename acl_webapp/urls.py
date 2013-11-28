from tornado.web import url

from handlers.pages import HomeHandler


url_patterns = [
    url(r"/", HomeHandler, name="home"),
]
