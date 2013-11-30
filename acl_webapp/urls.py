from tornado.web import url

from pages.handlers import HomeHandler
from accounts.handlers import RegisterHandler, LogoutHandler, LoginHandler


url_patterns = [
    url(r"/", HomeHandler, name="home"),
    url(r"/register/", RegisterHandler, name="register"),
    url(r"/logout/", LogoutHandler, name="logout"),
    url(r"/login/", LoginHandler, name="login"),
]
