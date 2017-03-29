from __future__ import unicode_literals, print_function, absolute_import

from scrapel import Request
from scrapel.decorators import spider_output_middleware

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['DepthMiddleware']

PRIORITY = 900


class DepthMiddleware(object):
    DEPTH_LIMIT = 0
    DEPTH_PRIORITY = 0

    @spider_output_middleware(priority=PRIORITY)
    def _depth_process_spider_output(self, response, result, settings):
        def _filter(request):
            if isinstance(request, Request):
                depth = response.meta['depth'] + 1
                request.meta['depth'] = depth
                if self.DEPTH_PRIORITY:
                    request.priority -= depth * self.DEPTH_PRIORITY
                if self.DEPTH_LIMIT and depth > self.DEPTH_LIMIT:
                    return False
            return True

        # base case (depth=0)
        if 'depth' not in response.meta:
            response.meta['depth'] = 0
        return (r for r in result or () if _filter(r))
