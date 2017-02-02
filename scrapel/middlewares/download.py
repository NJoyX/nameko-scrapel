from __future__ import unicode_literals, print_function, absolute_import

from .base import BaseMiddleware

__author__ = 'Fill Q'

__all__ = ['RequestMiddleware', 'ResponseMiddleware', 'ExceptionMiddleware']


# # @TODO remove obsolete
# PROCESS_REQUEST = 'download_request'
# PROCESS_RESPONSE = 'download_response'
# PROCESS_EXCEPTION = 'download_exception'


class RequestMiddleware(BaseMiddleware):
    def __init__(self, *args, **kwargs):
        super(RequestMiddleware, self).__init__(*args, **kwargs)


class ResponseMiddleware(BaseMiddleware):
    def __init__(self, *args, **kwargs):
        super(ResponseMiddleware, self).__init__(*args, **kwargs)


class ExceptionMiddleware(BaseMiddleware):
    def __init__(self, *args, **kwargs):
        super(ExceptionMiddleware, self).__init__(*args, **kwargs)
