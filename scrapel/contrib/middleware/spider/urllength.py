from __future__ import unicode_literals, print_function, absolute_import

from scrapel import Request
from scrapel.decorators import spider_output_middleware

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['UrlLengthMiddleware']

PRIORITY = 800


class UrlLengthMiddleware(object):
    URLLENGTH_LIMIT = 2083

    @spider_output_middleware(priority=PRIORITY)
    def _url_length_process_spider_output(self, response, result, settings):
        def _filter(request):
            if isinstance(request, Request) and len(request.url) > self.URLLENGTH_LIMIT:
                return False
            else:
                return True

        return (r for r in result or () if _filter(r))
