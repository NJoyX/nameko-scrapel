from __future__ import unicode_literals, print_function, absolute_import

import re

from scrapel import Request
from scrapel.constants import ALLOWED_DOMAINS
from scrapel.decorators import spider_output_middleware
from six.moves.urllib.parse import urlparse

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['OffsiteMiddleware']

PRIORITY = 500


class OffsiteMiddleware(object):
    domains_seen = set()

    @spider_output_middleware(priority=PRIORITY)
    def _offsite_process_spider_output(self, response, result, settings):
        for x in result:
            if isinstance(x, Request):
                if x.dont_filter or self._should_follow(x, settings):
                    yield x
                else:
                    domain = urlparse(x).hostname
                    if domain and domain not in self.domains_seen:
                        self.domains_seen.add(domain)
            else:
                yield x

    def _should_follow(self, request, settings):
        regex = self.get_host_regex(settings)
        # hostname can be None for wrong urls (like javascript links)
        host = urlparse(request).hostname or ''
        return bool(regex.search(host))

    @staticmethod
    def get_host_regex(settings):
        """Override this method to implement a different offsite policy"""
        allowed_domains = settings.get(ALLOWED_DOMAINS)
        if not allowed_domains:
            return re.compile('')  # allow all by default
        regex = r'^(.*\.)?(%s)$' % '|'.join(re.escape(d) for d in allowed_domains if d is not None)
        return re.compile(regex)
