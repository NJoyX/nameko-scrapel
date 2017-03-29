from __future__ import unicode_literals, print_function, absolute_import

from scrapel.decorators import spider_input_middleware, spider_exception_middleware
from scrapel.exceptions import IgnoreRequest

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['HttpErrorMiddleware']

PRIORITY = 50


class HttpError(IgnoreRequest):
    """A non-200 response was filtered"""

    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(HttpError, self).__init__(*args, **kwargs)


class HttpErrorMiddleware(object):
    HTTPERROR_ALLOW_ALL = False
    HTTPERROR_ALLOWED_CODES = []

    @spider_input_middleware(priority=PRIORITY)
    def _http_error_process_spider_input(self, response, settings):
        if 200 <= response.status < 300:  # common case
            return
        meta = response.meta
        if 'handle_httpstatus_all' in meta:
            return
        if 'handle_httpstatus_list' in meta:
            allowed_statuses = meta['handle_httpstatus_list']
        elif self.HTTPERROR_ALLOW_ALL:
            return
        else:
            allowed_statuses = self.HTTPERROR_ALLOWED_CODES
        if response.status in allowed_statuses:
            return
        raise HttpError(response, 'Ignoring non-200 response')

    @spider_exception_middleware(priority=PRIORITY)
    def _http_error_process_spider_exception(self, response, exception, settings):
        if isinstance(exception, HttpError):
            return []
