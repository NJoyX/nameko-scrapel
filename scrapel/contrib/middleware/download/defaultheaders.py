from __future__ import unicode_literals, print_function, absolute_import

from scrapel.decorators import request_middleware

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['DefaultHeadersMiddleware']

PRIORITY = 400


class DefaultHeadersMiddleware(object):
    DEFAULT_REQUEST_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en',
    }

    @request_middleware(priority=PRIORITY)
    def _default_headers_process_request(self, request, settings):
        for k, v in self.DEFAULT_REQUEST_HEADERS:
            if not all([k, v]):
                continue
            request.headers.setdefault(k, v)
