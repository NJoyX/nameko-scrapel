from __future__ import unicode_literals, print_function, absolute_import

from scrapel.exceptions import NotSupported
from scrapel.http import Request
from scrapel.http.headers import Headers
from six.moves.urllib.parse import urljoin

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['Response']


# @TODO JsonResponse


class Response(object):
    type = None

    def __init__(self, url, status=200, headers=None, body=b'', request=None):
        self.headers = Headers(headers or {})
        self.status = int(status)
        self._set_body(body)
        self._set_url(url)
        assert isinstance(
            request, Request
        ), 'Invalid request provided, must be an Request class instance, not {}'.format(type(request))
        self.request = request

    @property
    def meta(self):
        try:
            return self.request.meta
        except AttributeError:
            raise AttributeError(
                "Response.meta not available, this response "
                "is not tied to any request"
            )

    def _get_url(self):
        return self._url

    def _set_url(self, url):
        if isinstance(url, str):
            self._url = url
        else:
            raise TypeError('%s url must be str, got %s:' % (type(self).__name__,
                                                             type(url).__name__))

    url = property(_get_url, lambda self, url: None)

    def _get_body(self):
        return self._body

    def _set_body(self, body):
        if body is None:
            self._body = b''
        elif not isinstance(body, bytes):
            raise TypeError(
                "Response body must be bytes. "
                "If you want to pass unicode body use TextResponse "
                "or HtmlResponse.")
        else:
            self._body = body

    body = property(_get_body, lambda self, body: None)

    def __str__(self):
        return "<%d %s>" % (self.status, self.url)

    __repr__ = __str__

    def copy(self):
        """Return a copy of this Response"""
        return self.replace()

    def replace(self, *args, **kwargs):
        """Create a new Response with the same attributes except for those
        given new values.
        """
        for x in ['url', 'status', 'headers', 'body', 'request', 'flags']:
            kwargs.setdefault(x, getattr(self, x))
        cls = kwargs.pop('cls', self.__class__)
        return cls(*args, **kwargs)

    def urljoin(self, url):
        """Join this Response's url with a possible relative url to form an
        absolute interpretation of the latter."""
        return urljoin(self.url, url)

    @property
    def text(self):
        """For subclasses of TextResponse, this will return the body
        as text (unicode object in Python 2 and str in Python 3)
        """
        raise AttributeError("Response content isn't text")

    def css(self, *a, **kw):
        """Shortcut method implemented only by responses whose content
        is text (subclasses of TextResponse).
        """
        raise NotSupported("Response content isn't text")

    def xpath(self, *a, **kw):
        """Shortcut method implemented only by responses whose content
        is text (subclasses of TextResponse).
        """
        raise NotSupported("Response content isn't text")

    def follow(self, url, callback=None, method='GET', headers=None, body=None,
               cookies=None, meta=None, encoding='utf-8', priority=0,
               dont_filter=False, errback=None):
        """
        Return a :class:`~.Request` instance to follow a link ``url``.
        It accepts the same arguments as ``Request.__init__`` method,
        but ``url`` can be a relative URL or a ``scrapy.link.Link`` object,
        not only an absolute URL.

        :class:`~.TextResponse` provides a :meth:`~.TextResponse.follow`
        method which supports selectors in addition to absolute/relative URLs
        and Link objects.
        """
        url = self.urljoin(url)
        return Request(url, callback,
                       method=method,
                       headers=headers,
                       body=body,
                       cookies=cookies,
                       meta=meta,
                       encoding=encoding,
                       priority=priority,
                       dont_filter=dont_filter,
                       errback=errback)
