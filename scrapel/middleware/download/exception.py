from __future__ import unicode_literals, print_function, absolute_import

from scrapel.middleware.base import BaseMiddleware

from .collector import DownloadMiddlewareCollector

__author__ = 'Fill Q'

__all__ = ['ExceptionMiddleware']


class ExceptionMiddleware(BaseMiddleware):
    collector = DownloadMiddlewareCollector()

    def __init__(self, *args, **kwargs):
        super(ExceptionMiddleware, self).__init__(*args, **kwargs)
