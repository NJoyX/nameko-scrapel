from __future__ import unicode_literals, print_function, absolute_import

from scrapel import Request
from scrapel.constants import (
    MIDDLEWARE_SPIDER_INPUT_METHOD,
    MIDDLEWARE_SPIDER_OUTPUT_METHOD,
    MIDDLEWARE_SPIDER_EXCEPTION_METHOD
)
from scrapel.engine.mixin import ScrapelProvidersMixin
from scrapel.utils import get_callable, maybe_iterable

__author__ = 'Fill Q'
__all__ = ['ScrapelSpider']


class ScrapelSpider(ScrapelProvidersMixin):
    def __init__(self, worker, engine, settings):
        self.worker = worker
        self.engine = engine
        self.settings = settings

    @property
    def providers(self):
        return self.engine.providers

    @property
    def input_providers(self):
        return self._providers_by_method(MIDDLEWARE_SPIDER_INPUT_METHOD)

    @property
    def output_providers(self):
        return self._providers_by_method(MIDDLEWARE_SPIDER_OUTPUT_METHOD)

    @property
    def exception_providers(self):
        return self._providers_by_method(MIDDLEWARE_SPIDER_EXCEPTION_METHOD, reverse=True)

    def process_input(self, response):
        for provider in self.input_providers:
            _callback = get_callable(provider, 'process')
            if _callback is None:
                continue

            gt = self.worker.spawn(_callback, response=response, worker=self.worker, settings=self.settings)
            gt.link(self.filter_result, classes=(type(None), Exception))
            gt.link(self.pre_process_one)

            result = gt.wait()
            if isinstance(result, Exception):
                errback = get_callable(response.request, 'errback')
                if errback:
                    try:
                        new_result = errback(result)
                    except Exception as exc:
                        return self.process_exception(response=response, exception=exc)

                    return self.process_output(response=response, result=new_result)
        return  # @TODO call spider callback method

    def process_output(self, response, result):
        for provider in self.output_providers:
            _callback = get_callable(provider, 'process')
            if _callback is None:
                continue

            gt = self.worker.spawn(
                _callback,
                response=response,
                result=result,
                worker=self.worker,
                settings=self.settings
            )
            gt.link(self.filter_result, classes=(type(None), Exception))
            gt.link(self.pre_process_one)

            result = gt.wait()
            if isinstance(result, (dict, Request, Item)):
                return maybe_iterable(result)

    def process_exception(self, response, exception):
        pass
