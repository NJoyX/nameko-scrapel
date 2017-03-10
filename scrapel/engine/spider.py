from __future__ import unicode_literals, print_function, absolute_import

from scrapel.constants import (
    MIDDLEWARE_SPIDER_INPUT_METHOD,
    MIDDLEWARE_SPIDER_OUTPUT_METHOD,
    MIDDLEWARE_SPIDER_EXCEPTION_METHOD
)
from scrapel.engine.mixin import ScrapelProvidersMixin

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
    def spider_input_providers(self):
        return self._providers_by_method(MIDDLEWARE_SPIDER_INPUT_METHOD)

    @property
    def spider_output_providers(self):
        return self._providers_by_method(MIDDLEWARE_SPIDER_OUTPUT_METHOD)

    @property
    def spider_exception_providers(self):
        return self._providers_by_method(MIDDLEWARE_SPIDER_EXCEPTION_METHOD, reverse=True)

    def process_input(self, response):
        pass

    def process_output(self, response, result):
        pass

    def process_exception(self, response, exception):
        pass
