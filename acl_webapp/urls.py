from tornado.web import url

from pages.handlers import HomeHandler
from accounts.handlers import RegisterHandler, LogoutHandler, LoginHandler
from news.handlers import NewsListHandler, NewsCreateHandler,\
    NewsDetailHandler


url_patterns = [
    # pages
    url(r"/", HomeHandler, name="home"),

    # auth
    url(r"/register/", RegisterHandler, name="register"),
    url(r"/logout/", LogoutHandler, name="logout"),
    url(r"/login/", LoginHandler, name="login"),

    # news
    url(r"/news/", NewsListHandler, name="news_list"),
    url(r"/news/create/", NewsCreateHandler, name="news_create"),
    url(r"/news/detail/(?P<object_id>[0-9a-f]+)/", NewsDetailHandler,
        name="news_detail"),
]
