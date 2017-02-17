from __future__ import unicode_literals, print_function, absolute_import

from functools import partial

from lazy_object_proxy import Proxy as lazyProxy
from scrapel.constants import DOWNLOAD_METHOD
from scrapel.middleware.base import BaseMiddlewareCollector
from scrapel.utils import valid_providers

__author__ = 'Fill Q'
__all__ = ['DownloadMiddlewareCollector']


class DownloadMiddlewareCollector(BaseMiddlewareCollector):
    method = DOWNLOAD_METHOD

    @property
    def providers(self):
        return lazyProxy(partial(valid_providers, self._providers))

    def process(self, request, transport, settings, job_id):
        print(map(lambda m: (m.method, m.priority), self.providers), 'BOOOOOM', self.providers)
        print('Processing DL Middleware', self._providers, request)
