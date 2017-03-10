from __future__ import unicode_literals, print_function, absolute_import

from lazy_object_proxy import Proxy as lazyProxy

from nameko.extensions import ProviderCollector, SharedExtension
from scrapel.constants import MIDDLEWARE_METHODS
from scrapel.http.request import Request
from scrapel.http.response import Response
from scrapel.utils import maybe_iterable

from .downloader import ScrapelDownloader
from .spider import ScrapelSpider

__author__ = 'Fill Q'
__all__ = ['ScrapelEngine']


class ScrapelEngine(ProviderCollector, SharedExtension):
    def _valid_providers(self):
        from scrapel.middleware.base import MiddlewareBase

        return filter(
            lambda p: (isinstance(p, MiddlewareBase)
                       and getattr(p, 'method', None) in MIDDLEWARE_METHODS
                       and isinstance(getattr(p, 'priority', None), int)),
            maybe_iterable(self._providers)
        )

    # Providers collection
    @property
    def providers(self):
        return lazyProxy(self._valid_providers)

    # Processing
    def process_request(self, request, worker, settings):
        downloader = ScrapelDownloader(worker=worker, engine=self, settings=settings)
        gt = worker.spawn(downloader.process_request, request=request)
        gt.link(self.enqueue, worker=worker)

    def process_response(self, response, worker, settings):
        spider = ScrapelSpider(worker=worker, engine=self, settings=settings)
        gt = worker.spawn(spider.process_input, response=response)
        gt.link(self.enqueue, worker=worker)

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
