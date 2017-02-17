from __future__ import unicode_literals, print_function, absolute_import

from scrapel.middleware.base import BaseMiddleware

from .collector import SpiderMiddlewareCollector

__author__ = 'Fill Q'

__all__ = ['SpiderInputMiddleware']


class SpiderInputMiddleware(BaseMiddleware):
    collector = SpiderMiddlewareCollector()

    def __init__(self, *args, **kwargs):
        super(SpiderInputMiddleware, self).__init__(*args, **kwargs)
