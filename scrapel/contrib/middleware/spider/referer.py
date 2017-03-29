from __future__ import unicode_literals, print_function, absolute_import

from scrapel import Request
from scrapel.decorators import spider_output_middleware

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['RefererMiddleware']

PRIORITY = 700


class RefererMiddleware(object):
    REFERER_ENABLED = True

    @spider_output_middleware(priority=PRIORITY, enabled=REFERER_ENABLED)
    def _referer_process_spider_output(self, response, result, settings):
        def _set_referer(r):
            if isinstance(r, Request):
                r.headers.setdefault('Referer', response.url)
            return r

        return (_set_referer(r) for r in result or ())
