from __future__ import unicode_literals, print_function, absolute_import

from lazy_object_proxy import Proxy as lazyProxy

import eventlet
from nameko.extensions import ProviderCollector, SharedExtension
from scrapel import Request, Response
from scrapel.constants import MIDDLEWARE_METHODS
from scrapel.exceptions import ItemDropped
from scrapel.utils import maybe_iterable, iter_iterable
from werkzeug.utils import cached_property

from .downloader import ScrapelDownloader
from .spider import ScrapelSpider

__author__ = 'Fill Q'
__all__ = ['ScrapelEngine']


class ScrapelEngine(ProviderCollector, SharedExtension):
    @cached_property
    def _valid_providers(self):
        from scrapel.middleware.base import MiddlewareBase

        return filter(
            lambda p: (isinstance(p, MiddlewareBase)
                       and getattr(p, 'method', None) in MIDDLEWARE_METHODS
                       and isinstance(getattr(p, 'priority', None), int)
                       and getattr(p, 'enabled', False)),
            maybe_iterable(self._providers)
        )

    # Providers collection
    @property
    def providers(self):
        return lazyProxy(lambda: self._valid_providers)

    # Processing
    def process_request(self, request, worker, settings):
        downloader = ScrapelDownloader(worker=worker, engine=self, settings=settings)
        gt = worker.spawn(downloader.process_request, request=request)
        gt.link(self.enqueue, worker=worker)

    def process_response(self, response, worker, settings):
        spider = ScrapelSpider(worker=worker, engine=self, settings=settings)
        gt = worker.spawn(spider.process_input, response=response)
        gt.link(self.enqueue, worker=worker)

    def process_item(self, item, worker, settings):
        for pipeline in worker.pipeline:
            print(pipeline(item=item, settings=settings))
            result = None
            try:
                result = pipeline(item=item, settings=settings)
            except ItemDropped:
                pass
            except Exception as exc:
                event = eventlet.Event()
                worker.spawn(self.enqueue, event, worker=worker)
                event.send(exc)
            item = result if isinstance(result, type(item)) else item
        return item

    @staticmethod
    def enqueue(gt, worker):
        try:
            results = gt.wait()
        except Exception as exc:
            results = exc

        for result in iter_iterable(results):
            if isinstance(result, (Request, Response, worker.ScrapelItems)):
                worker.queue.put([result])
            elif isinstance(result, Exception):
                print(result)
