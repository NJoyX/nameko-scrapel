from nameko.extensions import Entrypoint, ProviderCollector, SharedExtension
from scrapel.collectors import ScrapelCollector
from scrapel.constants import MIDDLEWARE_METHODS

__author__ = 'Fill Q'

__all__ = ['BaseMiddleware']


def raise_notimplemented():
    raise NotImplementedError('Implement Collector')


class BaseMiddleware(Entrypoint):
    collector = property(lambda self: raise_notimplemented())
    priority = 99
    method = None

    def start(self):
        self.collector.register_provider(self)

    def stop(self):
        self.collector.unregister_provider(self)
        super(BaseMiddleware, self).stop()

    def __init__(self, method, priority=None):
        self.priority = priority or self.priority
        assert method in MIDDLEWARE_METHODS, 'Use only predefined methods'
        self.method = method


class BaseMiddlewareCollector(ProviderCollector, SharedExtension):
    method = None
    parent_collector = ScrapelCollector()

    def start(self):
        self.parent_collector.register_provider(self)

    def stop(self):
        self.parent_collector.unregister_provider(self)
        super(BaseMiddlewareCollector, self).stop()
