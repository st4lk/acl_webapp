# -*- coding: utf-8 -*-
from functools import wraps


def check_skip_permissions(func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        if self.skip_permissions:
            return True
        return func(self, *args, **kwargs)
    return wrapped
