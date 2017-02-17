from __future__ import unicode_literals, print_function, absolute_import

from scrapel.middleware.base import BaseMiddleware

from .collector import SpiderMiddlewareCollector

__author__ = 'Fill Q'

__all__ = ['SpiderOutputMiddleware']


class SpiderOutputMiddleware(BaseMiddleware):
    collector = SpiderMiddlewareCollector()

    def __init__(self, *args, **kwargs):
        super(SpiderOutputMiddleware, self).__init__(*args, **kwargs)
