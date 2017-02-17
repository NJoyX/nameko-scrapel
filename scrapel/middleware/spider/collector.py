from __future__ import unicode_literals, print_function, absolute_import

from functools import partial

from lazy_object_proxy import Proxy as lazyProxy
from scrapel.constants import SPIDER_METHOD
from scrapel.middleware.base import BaseMiddlewareCollector
from scrapel.utils import valid_providers

__author__ = 'Fill Q'
__all__ = ['SpiderMiddlewareCollector']


class SpiderMiddlewareCollector(BaseMiddlewareCollector):
    method = SPIDER_METHOD

    @property
    def providers(self):
        return lazyProxy(partial(valid_providers, self._providers))
