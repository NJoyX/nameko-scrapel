from __future__ import unicode_literals, print_function, absolute_import

from scrapel.middleware import (
    DownloaderRequestMiddleware,
    DownloaderResponseMiddleware,
    DownloaderExceptionMiddleware,
    SpiderInputMiddleware,
    SpiderOutputMiddleware,
    SpiderExceptionMiddleware
)

from .events import (
    on_start,
    on_stop,
    pipeline,
    start_requests
)

__author__ = 'Fill Q'
__all__ = [
    'request_middleware', 'response_middleware', 'exception_middleware',
    'spider_input_middleware', 'spider_output_middleware', 'spider_exception_middleware',
    'on_start', 'on_stop', 'pipeline', 'start_requests'
]

request_middleware = DownloaderRequestMiddleware.decorator
response_middleware = DownloaderResponseMiddleware.decorator
exception_middleware = DownloaderExceptionMiddleware.decorator
spider_input_middleware = SpiderInputMiddleware.decorator
spider_output_middleware = SpiderOutputMiddleware.decorator
spider_exception_middleware = SpiderExceptionMiddleware.decorator
