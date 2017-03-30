from __future__ import unicode_literals, print_function, absolute_import

from functools import partial

import types
from nameko.exceptions import IncorrectSignature
from nameko.extensions import Entrypoint, register_entrypoint
from scrapel.constants import (
    MIDDLEWARE_METHODS,
    MIDDLEWARE_DOWNLOADER_REQUEST_METHOD,
    MIDDLEWARE_DOWNLOADER_RESPONSE_METHOD,
    MIDDLEWARE_DOWNLOADER_EXCEPTION_METHOD,
    MIDDLEWARE_SPIDER_INPUT_METHOD,
    MIDDLEWARE_SPIDER_OUTPUT_METHOD,
    MIDDLEWARE_SPIDER_EXCEPTION_METHOD
)
from scrapel.engine import ScrapelEngine

__author__ = 'Fill Q'

__all__ = [
    'DownloaderRequestMiddleware', 'DownloaderResponseMiddleware', 'DownloaderExceptionMiddleware',
    'SpiderInputMiddleware', 'SpiderOutputMiddleware', 'SpiderExceptionMiddleware'
]


class MiddlewareBase(Entrypoint):
    collector = ScrapelEngine()
    priority = 9999
    method = None
    dispatch_uid = None
    enabled = None

    def start(self):
        self.collector.register_provider(self)

    def stop(self):
        self.collector.unregister_provider(self)
        super(MiddlewareBase, self).stop()

    def __init__(self, priority=None, enabled=None, dispatch_uid=None):
        assert self.method in MIDDLEWARE_METHODS, 'Use only predefined methods'
        assert isinstance(priority, (int, float, types.NoneType)), 'Priority must be only integer or float'
        self.priority = int(9999 if priority < 0 else priority)
        self.enabled = bool(True if enabled is None else enabled)
        self.dispatch_uid = dispatch_uid

    def process(self, worker, *args, **kwargs):
        try:
            self.check_signature(args, kwargs)
            service_cls = self.container.service_cls
            fn = getattr(service_cls, self.method_name)
            return fn(worker.context.service, *args, **kwargs)
        except IncorrectSignature:
            pass
        except Exception as exc:
            return exc

    @classmethod
    def decorator(cls, *args, **kwargs):
        def registering_decorator(fn, a, kw):
            instance = cls(*a, **kw)
            register_entrypoint(fn, instance)
            return fn

        if len(args) >= 1 and isinstance(args[0], types.FunctionType):
            return registering_decorator(args[0], a=args[1:], kw=kwargs)

        return partial(registering_decorator, a=args, kw=kwargs)


class DownloaderRequestMiddleware(MiddlewareBase):
    method = MIDDLEWARE_DOWNLOADER_REQUEST_METHOD


class DownloaderResponseMiddleware(MiddlewareBase):
    method = MIDDLEWARE_DOWNLOADER_RESPONSE_METHOD


class DownloaderExceptionMiddleware(MiddlewareBase):
    method = MIDDLEWARE_DOWNLOADER_EXCEPTION_METHOD


class SpiderInputMiddleware(MiddlewareBase):
    method = MIDDLEWARE_SPIDER_INPUT_METHOD


class SpiderOutputMiddleware(MiddlewareBase):
    method = MIDDLEWARE_SPIDER_OUTPUT_METHOD


class SpiderExceptionMiddleware(MiddlewareBase):
    method = MIDDLEWARE_SPIDER_EXCEPTION_METHOD
