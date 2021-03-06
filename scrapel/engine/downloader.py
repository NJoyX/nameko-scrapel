from __future__ import unicode_literals, print_function, absolute_import

import logging

from scrapel.constants import (
    MIDDLEWARE_DOWNLOADER_REQUEST_METHOD,
    MIDDLEWARE_DOWNLOADER_RESPONSE_METHOD,
    MIDDLEWARE_DOWNLOADER_EXCEPTION_METHOD
)
from scrapel.exceptions import IgnoreRequest
from scrapel.http.request import Request
from scrapel.http.response import Response
from scrapel.utils import get_callable

from .mixin import ScrapelProvidersMixin

__author__ = 'Fill Q'
__all__ = ['ScrapelDownloader']
logger = logging.getLogger(__name__)


class ScrapelDownloader(ScrapelProvidersMixin):
    def __init__(self, worker, engine):
        self.worker = worker
        self.engine = engine

    @property
    def settings(self):
        return self.worker.settings

    @property
    def transport(self):
        return self.worker.transport

    @property
    def providers(self):
        return self.engine.providers

    @property
    def request_providers(self):
        return self._providers_by_method(MIDDLEWARE_DOWNLOADER_REQUEST_METHOD)

    @property
    def response_providers(self):
        return self._providers_by_method(MIDDLEWARE_DOWNLOADER_RESPONSE_METHOD)

    @property
    def exception_providers(self):
        return self._providers_by_method(MIDDLEWARE_DOWNLOADER_EXCEPTION_METHOD, reverse=True)

    def process_request(self, request):
        for provider in self.request_providers:
            _callback = get_callable(provider, 'process')
            if _callback is None:
                continue

            gt = self.worker.spawn(_callback, request=request, worker=self.worker, settings=self.settings)
            gt.link(self.filter_result, classes=(type(None), Response, Request, IgnoreRequest))
            gt.link(self.pre_process_one)

            result = gt.wait()
            if isinstance(result, Request):
                return result
            elif isinstance(result, Response):
                return self.process_response(request=request, response=result)
            elif isinstance(result, IgnoreRequest):
                return self.process_exception(request=request, exception=result)

        gt2 = self.worker.spawn(self.download, request=request)
        gt2.link(self.pre_process_many)
        return gt2.wait()

    def process_response(self, request, response, dispatch_uid=None):
        providers = self.response_providers
        if dispatch_uid:
            providers = (self.filter_by_dispatch_uid(providers, dispatch_uid=dispatch_uid) +
                         self.next_in_chain(providers, dispatch_uid=dispatch_uid))

        _response = response
        for provider in providers:
            _callback = get_callable(provider, 'process')
            if _callback is None:
                continue

            gt = self.worker.spawn(
                _callback,
                request=request,
                response=_response,
                worker=self.worker,
                settings=self.settings
            )
            gt.link(self.filter_result, classes=(Response, Request, IgnoreRequest))
            gt.link(self.pre_process_one)

            result = gt.wait()
            if isinstance(result, Request):
                return result
            elif isinstance(result, Response):
                _response = result
            elif isinstance(result, IgnoreRequest):
                errback = get_callable(request, 'errback')
                if errback is None:
                    return

                errback(result)
                return

        return _response

    def process_exception(self, request, exception):
        logger.error('Downloader process exception.', extra={'stack': True})
        for provider in self.exception_providers:
            _callback = get_callable(provider, 'process')
            if _callback is None:
                continue

            gt = self.worker.spawn(
                _callback,
                request=request,
                exception=exception,
                worker=self.worker,
                settings=self.settings
            )
            gt.link(self.filter_result, classes=(type(None), Response, Request))
            gt.link(self.pre_process_one)

            result = gt.wait()
            if isinstance(result, Request):
                return result
            elif isinstance(result, Response):
                return self.process_response(
                    request=request,
                    response=result,
                    dispatch_uid=provider.dispatch_uid
                )

    def download(self, request):
        try:
            response = self.transport.make_response(request)
        except (NotImplemented, NotImplementedError):
            return
        except Exception as exc:
            logger.error('Download error', exc_info=True)
            return self.process_exception(request=request, exception=exc)
        return self.process_response(request=request, response=response)
