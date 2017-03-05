from __future__ import unicode_literals, print_function, absolute_import

__author__ = 'Fill Q'

__all__ = ['Request']


class Request(object):
    # @TODO implement errback

    def __init__(self, url, callback, headers=None, dont_filter=False):
        self.url = url
        self.callback = callback
        self.headers = headers
        self.dont_filter = bool(dont_filter)
