from __future__ import unicode_literals, print_function, absolute_import

import eventlet
from functools import partial
from lazy_object_proxy import Proxy as lazyProxy

from nameko.extensions import ProviderCollector, SharedExtension
from scrapel.constants import (
    MIDDLEWARE_DOWNLOADER_REQUEST_METHOD,
    MIDDLEWARE_DOWNLOADER_RESPONSE_METHOD,
    MIDDLEWARE_DOWNLOADER_EXCEPTION_METHOD,
    MIDDLEWARE_SPIDER_INPUT_METHOD,
    MIDDLEWARE_SPIDER_OUTPUT_METHOD,
    MIDDLEWARE_SPIDER_EXCEPTION_METHOD
)
from scrapel.exceptions import IgnoreRequest
from scrapel.request import Request
from scrapel.response import Response
from scrapel.utils import get_callable, valid_providers, maybe_iterable

from .downloader import ScrapelDownloader

__author__ = 'Fill Q'
__all__ = ['ScrapelEngine']


class ScrapelEngine(ProviderCollector, SharedExtension):
    # Providers collection
    @property
    def providers(self):
        return lazyProxy(partial(valid_providers, self._providers))

    @property
    def spider_input_providers(self):
        return self._providers_by_method(MIDDLEWARE_SPIDER_INPUT_METHOD)

    @property
    def spider_output_providers(self):
        return self._providers_by_method(MIDDLEWARE_SPIDER_OUTPUT_METHOD)

    @property
    def spider_exception_providers(self):
        return self._providers_by_method(MIDDLEWARE_SPIDER_EXCEPTION_METHOD, reverse=True)

    # Processing
    def process_request(self, request, worker, settings):
        downloader = ScrapelDownloader(worker=worker, engine=self)
        gt = worker.spawn(downloader.process_request, request=request, settings=settings)
        gt.link(self.enqueue, worker=worker)

    def process_response(self, response, worker, settings):
        request = response.request
        for spm in self.spider_middlewares:
            _callback = get_callable(spm, 'process')
            if _callback is None:
                continue
            gt = worker.spawn(_callback, response=response, request=request, worker=worker, settings=settings)
            gt.link(self.post_process, worker=worker)

    def process_item(self, item, settings):
        pass

    @staticmethod
    def enqueue(gt, worker):
        try:
            result = gt.wait()
        except Exception as exc:
            result = exc

        if isinstance(result, (Request, Response)):  # , Item)):
            worker.queue.put(result)
        elif isinstance(result, Exception):
            print(result)
