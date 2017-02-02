from nameko.extensions import Entrypoint
from scrapel.collector import ScrapelMiddlewareCollector

__author__ = 'Fill Q'

__all__ = ['BaseMiddleware']


class BaseMiddleware(Entrypoint):
    collector = ScrapelMiddlewareCollector()
    priority = 99

    def start(self):
        self.collector.register_provider(self)

    def stop(self):
        self.collector.unregister_provider(self)
        super(BaseMiddleware, self).stop()

    def __init__(self, priority=None):
        self.priority = priority or self.priority
