import logging
import tornado.web
from settings import jinja_env

logger = logging.getLogger('edtr_logger')


class BaseHandler(tornado.web.RequestHandler):
    """A class to collect common handler methods - all other handlers should
    subclass this one.
    """

    def render(self, template, context=None):
        """Renders template using jinja2"""
        if not context:
            context = {}
        context.update(self.get_template_namespace())
        self.write(jinja_env.get_template(template).render(context))
        # Always set _xsrf cookie
        self.xsrf_token
        self.flush()
