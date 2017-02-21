from __future__ import unicode_literals, print_function, absolute_import

from scrapel.middleware.base import BaseMiddleware

from .collector import DownloadMiddlewareCollector

__author__ = 'Fill Q'

__all__ = ['RequestMiddleware']


class RequestMiddleware(BaseMiddleware):
    collector = DownloadMiddlewareCollector()

    # def __init__(self, priority=9999, *args, **kwargs):
    #     # self.method = method
    #     print(args, kwargs)
    #     self.priority = priority
    #     super(RequestMiddleware, self).__init__(*args, **kwargs)
