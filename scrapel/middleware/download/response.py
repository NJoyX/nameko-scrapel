from __future__ import unicode_literals, print_function, absolute_import

from scrapel.middleware.base import BaseMiddleware

from .collector import DownloadMiddlewareCollector

__author__ = 'Fill Q'

__all__ = ['ResponseMiddleware']


class ResponseMiddleware(BaseMiddleware):
    collector = DownloadMiddlewareCollector()

    def __init__(self, *args, **kwargs):
        super(ResponseMiddleware, self).__init__(*args, **kwargs)
