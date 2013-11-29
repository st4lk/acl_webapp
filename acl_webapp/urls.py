from tornado.web import url

from pages.handlers import HomeHandler
from accounts.handlers import RegisterHandler


url_patterns = [
    url(r"/", HomeHandler, name="home"),
    url(r"/register/", RegisterHandler, name="register"),
]
