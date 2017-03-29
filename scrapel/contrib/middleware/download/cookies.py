from __future__ import unicode_literals, print_function, absolute_import

from collections import defaultdict

import six
from scrapel import Response
from scrapel.decorators import request_middleware, response_middleware
from scrapel.http.cookies import CookieJar

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['CookiesMiddleware']

PRIORITY = 700


class CookiesMiddleware(object):
    COOKIES_ENABLED = False
    jars = defaultdict(CookieJar)

    @request_middleware(priority=PRIORITY, enabled=COOKIES_ENABLED)
    def _cookies_process_request(self, request, settings):
        if request.meta.get('dont_merge_cookies', False):
            return

        cookiejarkey = request.meta.get("cookiejar")
        jar = self.jars[cookiejarkey]
        cookies = self._get_request_cookies(jar, request)
        for cookie in cookies:
            jar.set_cookie_if_ok(cookie, request)

        # set Cookie header
        request.headers.pop('Cookie', None)
        jar.add_cookie_header(request)
        # @TODO debug cookie

    @response_middleware(priority=PRIORITY, enabled=COOKIES_ENABLED)
    def _cookies_process_response(self, request, response, settings):
        if request.meta.get('dont_merge_cookies', False):
            return response

        # extract cookies from Set-Cookie and drop invalid/expired cookies
        cookiejarkey = request.meta.get("cookiejar")
        jar = self.jars[cookiejarkey]
        jar.extract_cookies(response, request)
        # @TODO debug cookie
        return response


    @staticmethod
    def _format_cookie(cookie):
        # build cookie string
        cookie_str = '%s=%s' % (cookie['name'], cookie['value'])

        if cookie.get('path', None):
            cookie_str += '; Path=%s' % cookie['path']
        if cookie.get('domain', None):
            cookie_str += '; Domain=%s' % cookie['domain']

        return cookie_str

    def _get_request_cookies(self, jar, request):
        if isinstance(request.cookies, dict):
            cookie_list = [{'name': k, 'value': v} for k, v in six.iteritems(request.cookies)]
        else:
            cookie_list = request.cookies

        cookies = [self._format_cookie(x) for x in cookie_list]
        headers = {'Set-Cookie': cookies}
        response = Response(request.url, headers=headers)

        return jar.make_cookies(response, request)
