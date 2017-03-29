from __future__ import unicode_literals, print_function, absolute_import

import zlib

from scrapel import Response, TextResponse
from scrapel.decorators import request_middleware, response_middleware
from scrapel.http.responsetypes import responsetypes
from scrapel.utils.gz import is_gzipped, gunzip

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['HttpCompressionMiddleware']

PRIORITY = 590


class HttpCompressionMiddleware(object):
    """This middleware allows compressed (gzip, deflate) traffic to be
    sent/received from web sites"""
    COMPRESSION_ENABLED = True

    @request_middleware(priority=PRIORITY, enabled=COMPRESSION_ENABLED)
    def _http_compression_process_request(self, request, settings):
        request.headers.setdefault('Accept-Encoding', 'gzip,deflate')

    @response_middleware(priority=PRIORITY, enabled=COMPRESSION_ENABLED)
    def _http_compression_process_response(self, request, response, settings):
        if request.method == 'HEAD':
            return response
        if isinstance(response, Response):
            content_encoding = response.headers.getlist('Content-Encoding')
            if content_encoding and not is_gzipped(response):
                encoding = content_encoding.pop()
                decoded_body = self._decode(response.body, encoding.lower())
                respcls = responsetypes.from_args(headers=response.headers, url=response.url)
                kwargs = dict(cls=respcls, body=decoded_body)
                if issubclass(respcls, TextResponse):
                    # force recalculating the encoding until we make sure the
                    # responsetypes guessing is reliable
                    kwargs['encoding'] = None
                response = response.replace(**kwargs)
                if not content_encoding:
                    del response.headers['Content-Encoding']

        return response

    @staticmethod
    def _decode(body, encoding):
        if encoding == b'gzip' or encoding == b'x-gzip':
            body = gunzip(body)

        if encoding == b'deflate':
            try:
                body = zlib.decompress(body)
            except zlib.error:
                # ugly hack to work with raw deflate content that may
                # be sent by microsoft servers. For more information, see:
                # http://carsten.codimi.de/gzip.yaws/
                # http://www.port80software.com/200ok/archive/2005/10/31/868.aspx
                # http://www.gzip.org/zlib/zlib_faq.html#faq38
                body = zlib.decompress(body, -15)
        return body
