from __future__ import unicode_literals, print_function, absolute_import

from functools import partial
from lazy_object_proxy import Proxy as lazyProxy

from scrapel.constants import (
    DOWNLOAD_METHOD,
    MIDDLEWARE_REQUEST_METHOD,
    MIDDLEWARE_RESPONSE_METHOD,
    MIDDLEWARE_EXCEPTION_METHOD
)
from scrapel.middleware.base import BaseMiddlewareCollector
from scrapel.utils import valid_providers

__author__ = 'Fill Q'
__all__ = ['DownloadMiddlewareCollector']


class DownloadMiddlewareCollector(BaseMiddlewareCollector):
    method = DOWNLOAD_METHOD
    _sort_key = (lambda self, p: p.priority or p.__class__.__name__)

    @property
    def providers(self):
        return lazyProxy(partial(valid_providers, self._providers))

    def _providers_by_method(self, method):
        return filter(lambda p: p.method == method, self.providers)

    @property
    def request_providers(self):
        return sorted(self._providers_by_method(MIDDLEWARE_REQUEST_METHOD), key=self._sort_key)

    @property
    def response_providers(self):
        return sorted(self._providers_by_method(MIDDLEWARE_RESPONSE_METHOD), key=self._sort_key)

    @property
    def exception_providers(self):
        return sorted(self._providers_by_method(MIDDLEWARE_EXCEPTION_METHOD), key=self._sort_key, reverse=True)

    def process(self, request, transport, settings, job_id, ctx):
        # for provider in self.request_providers:
        #     print(provider.priority)
        # print(dir(self.container))
        # print(map(lambda m: (m.method, m.priority), self.providers), 'BOOOOOM', self.providers)
        # print('Processing DL Middleware', self._providers, request)
        # print(self.providers[0].method, ctx.service)
        # print(self.request_providers, self.response_providers, self.exception_providers)
        print(settings)
