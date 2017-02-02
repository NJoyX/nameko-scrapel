from __future__ import unicode_literals, print_function, absolute_import

from .base import BaseMiddleware

__author__ = 'Fill Q'

__all__ = ['SpiderInputMiddleware', 'SpiderOutputMiddleware', 'SpiderExceptionMiddleware']


# # @TODO remove obsolete
# PROCESS_INPUT = 'spider_input'
# PROCESS_OUTPUT = 'spider_output'
# PROCESS_EXCEPTION = 'spider_exception'


class SpiderInputMiddleware(BaseMiddleware):
    def __init__(self, *args, **kwargs):
        super(SpiderInputMiddleware, self).__init__(*args, **kwargs)


class SpiderOutputMiddleware(BaseMiddleware):
    def __init__(self, *args, **kwargs):
        super(SpiderOutputMiddleware, self).__init__(*args, **kwargs)


class SpiderExceptionMiddleware(BaseMiddleware):
    def __init__(self, *args, **kwargs):
        super(SpiderExceptionMiddleware, self).__init__(*args, **kwargs)
