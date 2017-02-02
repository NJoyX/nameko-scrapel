from __future__ import unicode_literals, print_function, absolute_import

import urllib3

from .base import BaseTransport

__author__ = 'Fill Q'


class Urllib3Transport(BaseTransport):
    klass = urllib3.PoolManager

    def __init__(self, config, ):
        self.config = config
