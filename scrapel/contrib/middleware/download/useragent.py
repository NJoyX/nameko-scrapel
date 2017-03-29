from __future__ import unicode_literals, print_function, absolute_import

import sys

import six
from scrapel.decorators import request_middleware

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['UserAgentMiddleware']

PRIORITY = 500


class UserAgentMiddleware(object):
    USER_AGENT = None

    @request_middleware(priority=PRIORITY)
    def _user_agent_process_request(self, request, settings):
        _default = 'Python-scrapel/{}'.format('.'.join(map(six.text_type, sys.version_info[:3])))
        _agent = self.USER_AGENT if isinstance(self.USER_AGENT, (six.text_type,) + six.string_types) else _default
        request.headers.setdefault(b'User-Agent', _agent)
