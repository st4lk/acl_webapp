ACL async application
=====================

Application with permissions system (ACL). Built with python, tornado, mongodb, motor.

[![Build Status](https://travis-ci.org/st4lk/acl_webapp.png?branch=master)](https://travis-ci.org/st4lk/acl_webapp) [![Coverage Status](https://coveralls.io/repos/st4lk/acl_webapp/badge.png?branch=master)](https://coveralls.io/r/st4lk/acl_webapp?branch=master)



Supports
--------

- python 2.7


Installation
------------

- install mognodb: [http://www.mongodb.org/downloads](http://www.mongodb.org/downloads) (tested on 2.4.8)
- start mongod process
- clone this repo
- install dependencies:
    
    pip install -r requirements.txt

- start local server (`--debug=True` will cause debug mode):

    python app.py

- access http://127.0.0.1:8888/


Description
-----------
### Structure
Project has django-like structure: it contains 'applications'.
Application has handlers, models, forms, etc.

### Base modules
Base handlers module have ListHandler, DetailHandler, CreateHandler, DeleteHandler.
They behave similiar to django ListView, DetailView and so on.

Base models module have BaseModel with common used methods. All models should subclass it.

Base forms contains adopted to tornado Form and ModelForm (subclasses of WTForms). ModelForm performs validation on its model and provide model object, if validation pass.

### Permission system
Permissions are base on models.
Each user has 'permissions' field, which has following structure:

    permissions = {
        'model_name_1': ['read',],
        'model_name_2': ['read', 'write'],
        'model_name_3': ['read', 'write', 'delete'],
    }

So user with such permissions can read objects of `model_name_1`, can read and write objects of `model_name_2` and can read, write and delete objects of `model_name_3`.
Permissions are checked in base handlers, so it is needed to subclass them.
Example:

    from base.handlers import ListHandler
    from .models import NewsModel

    class NewsListHandler(ListHandler):

        def initialize(self, **kwargs):
            super(NewsListHandler, self).initialize(**kwargs)
            self.model = NewsModel
            self.template_name = "news/list.html"

If it is needed to check additional permissions, it can be done by overriding corresponding methods of base handler. The easiest way is to provide it in `get_additional_permissions` method. For more complicated behaviour look at base handlers implementation.

Example, where to be able to delete 'news' object user must be also an author of this object (in addition to 'delete' permission):

    from base.handlers import DeleteHandler
    from .models import NewsModel

    class NewsDeleteHandler(DeleteHandler):
        # ...

        @gen.coroutine
        def get_additional_permissions(self):
            if self.object is None:
                yield self.get_object()
            news = self.object
            raise gen.Return(news.author == self.current_user)
