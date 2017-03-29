from __future__ import unicode_literals, print_function, absolute_import

from scrapel import HtmlResponse
from scrapel.decorators import response_middleware
from scrapel.exceptions import IgnoreRequest
from six.moves.urllib.parse import urljoin
from w3lib.html import get_meta_refresh
from w3lib.url import safe_url_string

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['RedirectMiddleware', 'MetaRefreshMiddleware']


class BaseRedirectMiddleware(object):
    REDIRECT_MAX_TIMES = 20
    REDIRECT_PRIORITY_ADJUST = +2

    def _redirect(self, redirected, request, reason):
        ttl = request.meta.setdefault('redirect_ttl', self.REDIRECT_MAX_TIMES)
        redirects = request.meta.get('redirect_times', 0) + 1

        if ttl and redirects <= self.REDIRECT_MAX_TIMES:
            redirected.meta['redirect_times'] = redirects
            redirected.meta['redirect_ttl'] = ttl - 1
            redirected.meta['redirect_urls'] = request.meta.get('redirect_urls', []) + \
                                               [request.url]
            redirected.dont_filter = request.dont_filter
            redirected.priority = request.priority + self.REDIRECT_PRIORITY_ADJUST
            return redirected
        else:
            raise IgnoreRequest("max redirections reached")

    @staticmethod
    def _redirect_request_using_get(request, redirect_url):
        redirected = request.replace(url=redirect_url, method='GET', body='')
        redirected.headers.pop('Content-Type', None)
        redirected.headers.pop('Content-Length', None)
        return redirected


class RedirectMiddleware(BaseRedirectMiddleware):
    """Handle redirection of requests based on response status and meta-refresh html tag"""
    HANDLE_HTTPSTATUS_LIST = []

    @response_middleware(priority=600)
    def _redirect_process_response(self, request, response, settings):
        if (request.meta.get('dont_redirect', False) or
                    response.status in self.HANDLE_HTTPSTATUS_LIST or
                    response.status in request.meta.get('handle_httpstatus_list', []) or
                request.meta.get('handle_httpstatus_all', False)):
            return response

        allowed_status = (301, 302, 303, 307)
        if 'Location' not in response.headers or response.status not in allowed_status:
            return response

        location = safe_url_string(response.headers['location'])

        redirected_url = urljoin(request.url, location)

        if response.status in (301, 307) or request.method == 'HEAD':
            redirected = request.replace(url=redirected_url)
            return self._redirect(redirected, request, response.status)

        redirected = self._redirect_request_using_get(request, redirected_url)
        return self._redirect(redirected, request, response.status)


class MetaRefreshMiddleware(BaseRedirectMiddleware):
    REDIRECT_MAX_METAREFRESH_DELAY = METAREFRESH_MAXDELAY = 100

    @response_middleware(priority=580)
    def _meta_refresh_process_response(self, request, response, settings):
        if request.meta.get('dont_redirect', False) or request.method == 'HEAD' or \
                not isinstance(response, HtmlResponse):
            return response

        if isinstance(response, HtmlResponse):
            interval, url = get_meta_refresh(response)
            if url and interval < self.REDIRECT_MAX_METAREFRESH_DELAY:
                redirected = self._redirect_request_using_get(request, url)
                return self._redirect(redirected, request, 'meta refresh')

        return response
