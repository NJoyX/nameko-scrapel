from __future__ import unicode_literals, print_function, absolute_import

import eventlet

from .collectors import ScrapelCollector
from .constants import JOBID
from .request import Request
from .response import Response
from .settings import Settings
from .transport import Urllib3Transport
from .utils import maybe_iterable

__author__ = 'Fill Q'
__all__ = ['ScrapelWorker']


class ScrapelWorker(object):
    collector = ScrapelCollector()

    def __init__(self, context, job_id, start_requests_func, transport=Urllib3Transport):
        self.context = context
        self.job_id = job_id
        self.start_requests_func = start_requests_func
        self.transport = transport

        self.settings = Settings()
        self.settings.setdefault(JOBID, self.job_id)
        self.collector = self.collector.bind(self.container)
        self.event = eventlet.Event()
        self.pool = eventlet.GreenPool()
        self.queue = eventlet.Queue()
        self.results = set()

    @property
    def container(self):
        return self.context.container

    @property
    def config(self):
        return self.context.config

    @property
    def is_running(self):
        return self.event.ready() is False

    def stop(self, result=None):
        if self.is_running:
            self.event.send(result)
            self.pool.waitall()
            # self.container._died.send(None)

    def spawn(self, fn, *args, **kwargs):
        if not callable(fn):
            fn = lambda *a, **kw: None
        return self.pool.spawn(fn, *args, **kwargs)

    def pile(self, fn, *args, **kwargs):
        if not callable(fn):
            fn = lambda *a, **kw: None
        _pile = eventlet.GreenPile(self.pool)
        _pile.spawn(fn, *args, **kwargs)
        return maybe_iterable(_pile)

    def map(self, fn, *args, **kwargs):
        if not callable(fn):
            fn = lambda *a, **kw: None
        _map = eventlet.greenpool.GreenMap(self.pool)
        _map.spawn(fn, *args, **kwargs)
        return maybe_iterable(_map)

    def run(self):
        self.queue.put(self.pile(self.start_requests_func, self.context.service))

        while True:
            if not self.is_running:
                break

            while not self.queue.empty():
                items = self.queue.get()
                # processing items
                gt = self.spawn(self.process, items)
                gt.link(lambda result: self.update_results(result.wait()))
            self.pool.waitall()
            if self.queue.empty():
                self.stop(self.results)

        return self.event.wait()

    def process(self, items):
        results = []
        for item in maybe_iterable(items):
            result = None
            if isinstance(item, Request):
                result = self.pile(self.collector.process_request, request=item, transport=self.transport,
                                   worker=self, settings=self.settings.copy())
            elif isinstance(item, Response):
                result = self.pile(self.collector.process_response,
                                   response=item, worker=self, settings=self.settings.copy())
            # @TODO implement for pipeline
            # elif isinstance(item, ScrapelItem):
            #     result = self.spawn(self.collector.process_item, item=item, settings=self.settings)
            results.extend(list(maybe_iterable(result)))
        return filter(None, results)

    def update_results(self, result):
        self.results.update(filter(None, maybe_iterable(result)))
