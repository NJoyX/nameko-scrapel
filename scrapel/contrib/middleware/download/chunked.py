from __future__ import unicode_literals, print_function, absolute_import

from scrapel.decorators import response_middleware

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['ChunkedTransferMiddleware']

PRIORITY = 830


class ChunkedTransferMiddleware(object):
    """This middleware adds support for chunked transfer encoding, as
    documented in: http://en.wikipedia.org/wiki/Chunked_transfer_encoding
    """

    @response_middleware(priority=PRIORITY)
    def _chunked_process_response(self, request, response, settings):
        if response.headers.get('Transfer-Encoding') == 'chunked':
            body = self._decode_chunked_transfer(response.body)
            return response.replace(body=body)
        return response

    @staticmethod
    def _decode_chunked_transfer(chunked_body):
        """Parsed body received with chunked transfer encoding, and return the
        decoded body.

        For more info see:
        http://en.wikipedia.org/wiki/Chunked_transfer_encoding

        """
        body, h, t = '', '', chunked_body
        while t:
            h, t = t.split('\r\n', 1)
            if h == '0':
                break
            size = int(h, 16)
            body += t[:size]
            t = t[size + 2:]
        return body
