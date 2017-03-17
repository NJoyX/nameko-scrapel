from __future__ import unicode_literals, print_function, absolute_import

import six
from scrapel.http.headers import Headers
from six.moves.urllib.parse import urldefrag
from w3lib.url import safe_url_string, add_or_replace_parameter
from w3lib.util import to_bytes

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['Request']


class Request(object):
    def __init__(self, url, callback, method='GET', headers=None, body=None,
                 cookies=None, meta=None, encoding='utf-8', priority=0,
                 dont_filter=False, errback=None):

        self._encoding = encoding  # this one has to be set first
        self.method = str(method).upper()
        self._set_url(url)
        self._set_body(body)
        assert isinstance(priority, int), "Request priority not an integer: %r" % priority
        self.priority = priority

        assert callback or not errback, "Cannot use errback without a callback"
        self.callback = callback
        self.errback = errback

        self.cookies = cookies or {}
        self.headers = Headers(headers or {}, encoding=encoding)
        self.dont_filter = dont_filter

        self._meta = dict(meta) if meta else None

    @property
    def meta(self):
        if self._meta is None:
            self._meta = {}
        return self._meta

    @staticmethod
    def _escape_ajax(url):
        defrag, frag = urldefrag(url)
        if not frag.startswith('!'):
            return url
        return add_or_replace_parameter(defrag, '_escaped_fragment_', frag[1:])

    def _get_url(self):
        return self._url

    def _set_url(self, url):
        if not isinstance(url, six.string_types):
            raise TypeError('Request url must be str or unicode, got %s:' % type(url).__name__)

        s = safe_url_string(url, self.encoding)
        self._url = self._escape_ajax(s)

        if ':' not in self._url:
            raise ValueError('Missing scheme in request url: %s' % self._url)

    url = property(_get_url, lambda self, url: None)

    def _get_body(self):
        return self._body

    def _set_body(self, body):
        if body is None:
            self._body = b''
        else:
            self._body = to_bytes(body, self.encoding)

    body = property(_get_body, lambda self, body: None)

    @property
    def encoding(self):
        return self._encoding

    def __str__(self):
        return "<Request: %s %s>" % (self.method, self.url)

    __repr__ = __str__

    def copy(self):
        """Return a copy of this Request"""
        return self.replace()

    def replace(self, *args, **kwargs):
        """Create a new Request with the same attributes except for those
        given new values.
        """
        for x in ['url', 'method', 'headers', 'body', 'cookies', 'meta',
                  'encoding', 'priority', 'dont_filter', 'callback', 'errback']:
            kwargs.setdefault(x, getattr(self, x))
        cls = kwargs.pop('cls', self.__class__)
        return cls(*args, **kwargs)
