from __future__ import unicode_literals, print_function, absolute_import

from functools import partial

import eventlet

from .collector import ScrapelMiddlewareCollector
from .transport import Urllib3Transport
from .utils import maybe_iterable
from .settings import Settings

__author__ = 'Fill Q'


class ScrapelWorker(object):
    settings = Settings()

    collector = ScrapelMiddlewareCollector()
    pool = eventlet.GreenPool(1)
    rQueue = eventlet.Queue(1)
    finish = eventlet.Event()

    def __init__(self, max_workers, start_requests_func, transport=Urllib3Transport):
        self.context = None
        self.max_workers = max_workers
        self.start_requests_func = start_requests_func
        self.transport = transport
        self.rQueue.resize(self.max_workers)
        self.pool.resize(self.max_workers)
        self._running = False

    def setup(self, context):
        self.context = context
        self.collector = self.collector.bind(self.container)

    @property
    def container(self):
        return self.context.container

    @property
    def config(self):
        return self.context.config

    @property
    def free(self):
        return self.pool.free()

    def stop(self):
        self._running = False
        if not self.finish.ready():
            self.finish.send(None)
        self.pool.waitall()
        # self.container._died.send(None)

    def run(self, job_id):
        self._running = True

        pile = eventlet.greenpool.GreenPile(self.pool)
        pile.spawn(partial(self.start_requests_func, self.context.service))
        self.rQueue.put_nowait(pile)

        while True:
            if self.finish.ready():
                break

            while not self.rQueue.empty():
                items = self.rQueue.get()
                # process item
                self.pool.spawn_n(self.process, items, job_id, self.rQueue)
            self.pool.waitall()
            if self.rQueue.empty():
                self.stop()
                break
        return job_id

    def process(self, items, job_id, queue):
        results = []
        settings = self.settings.copy()
        settings['JOBID'] = job_id
        for item in maybe_iterable(items):
            if hasattr(item, 'process'):
                results.append(item.process(collector=self.collector, context=self.context, settings=settings))
        return filter(None, results)
