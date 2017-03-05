from __future__ import unicode_literals, print_function, absolute_import

import eventlet
from sortedcontainers import SortedSet

from .engine import ScrapelEngine
from .constants import JOBID
from .request import Request
from .response import Response
from .settings import Settings
from .transport import Urllib3Transport
from .utils import maybe_iterable, FunctionGetMixin

__author__ = 'Fill Q'
__all__ = ['ScrapelWorker', 'FakeWorker']

DEFAULT_SET_LOAD = 10000


class ScrapelWorker(FunctionGetMixin):
    engine = ScrapelEngine()

    def __init__(self, context, job_id, transport=Urllib3Transport, **extra):
        self.context = context
        self.jid = job_id
        self.transport = transport

        self.settings = Settings()
        self.settings.setdefault(JOBID, self.jid)
        self.settings.update(extra)
        self.engine = self.engine.bind(self.container)
        self.event = eventlet.Event()
        self.pool = eventlet.GreenPool()
        self.queue = eventlet.Queue()
        self.results = self.defaultset

    @property
    def defaultset(self):
        return SortedSet(load=DEFAULT_SET_LOAD)

    @property
    def container(self):
        return self.context.container

    @property
    def config(self):
        return self.context.config

    @property
    def service(self):
        return self.context.service

    @property
    def is_running(self):
        return self.event.ready() is False

    def stop(self, result=None):
        if result is None:
            result = self.defaultset

        if self.is_running:
            self.event.send(result)

        self.map(self.on_stop, results=set(
            self.event.wait() or self.defaultset | result | self.results
        ), jid=self.jid)
        self.pool.waitall()

    def spawn(self, fn, *args, **kwargs):
        if not callable(fn):
            fn = (lambda *a, **kw: None)
        return self.pool.spawn(fn, *args, **kwargs)

    def pile(self, fn, *args, **kwargs):
        if not callable(fn):
            fn = (lambda *a, **kw: [])
        _pile = eventlet.GreenPile(self.pool)
        _pile.spawn(fn, *args, **kwargs)
        return maybe_iterable(_pile)

    def map(self, fn, *args, **kwargs):
        if not callable(fn):
            fn = (lambda *a, **kw: [])
        _map = eventlet.greenpool.GreenMap(self.pool)
        _map.spawn(fn, *args, **kwargs)
        return maybe_iterable(_map)

    def run(self, gt):
        self.queue.put(self.pile(self.start_requests, jid=self.jid))

        while True:
            if not self.is_running:
                break

            while not self.queue.empty():
                items = self.queue.get()
                # processing items
                _gt = self.spawn(self.process, items)
                _gt.link(self.update_results)
            self.pool.waitall()
            if self.queue.empty():
                self.stop(self.results)

        return self.event.wait()

    def process(self, items):
        results = []
        for item in maybe_iterable(items):
            result = None
            if isinstance(item, Request):
                self.engine.process_request(request=item, worker=self, settings=self.settings)
            elif isinstance(item, Response):
                self.engine.process_response(response=item, worker=self, settings=self.settings)
            # @TODO implement for pipeline
            # elif isinstance(item, ScrapelItem):
            #     result = self.spawn(self.engine.process_item, item=item, settings=self.settings)
            results.extend(maybe_iterable(result))
        return filter(None, results)

    def update_results(self, gt):
        self.results.update(filter(None, maybe_iterable(gt.wait())))


class FakeWorker(FunctionGetMixin):
    @property
    def service(self):
        return

    def stop(self, *args, **kwargs):
        pass
