from __future__ import unicode_literals, print_function, absolute_import

import collections
from lazy_object_proxy import Proxy as lazyProxy

import eventlet
import types
from sortedcontainers import SortedSet

from .constants import JOBID, ALLOWED_DOMAINS
from .engine import ScrapelEngine
from .http.request import Request
from .http.response import Response
from .settings import Settings
from .utils import maybe_iterable, iter_iterable, FunctionGetMixin

__author__ = 'Fill Q'
__all__ = ['ScrapelWorker', 'FakeWorker']

DEFAULT_SET_LOAD = 1000


class ScrapelWorker(FunctionGetMixin):
    engine = ScrapelEngine()
    ScrapelItems = (dict, collections.Mapping)

    def __init__(self, context, job_id, allowed_domains, transport_cls, **extra):
        self.context = context
        self.jid = job_id

        self.settings = Settings()
        self.settings.setdefault(JOBID, self.jid)
        self.settings.setdefault(ALLOWED_DOMAINS, allowed_domains)
        self.settings.setdefault('PROCESS_UID', self.context.call_id)
        self.settings.update(extra)
        self.engine = self.engine.bind(self.container)
        self.event = eventlet.Event()
        self.pool = eventlet.GreenPool()
        self.queue = eventlet.Queue()
        self.results = self.defaultset
        self.transport = transport_cls(worker=self, settings=lazyProxy(lambda: self.settings))

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

        self.map(self.on_stop, results=SortedSet(
            self.event.wait() or self.defaultset | result | self.results,
            load=DEFAULT_SET_LOAD
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

    def run(self, gt, *args, **kwargs):
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
        for item in iter_iterable(items):
            if isinstance(item, Request):
                self.engine.process_request(request=item, worker=self)
            elif isinstance(item, Response):
                self.engine.process_response(response=item, worker=self)
            elif isinstance(item, self.ScrapelItems):
                result = self.engine.process_item(item=item, worker=self)
                results.extend(maybe_iterable(result))
            elif isinstance(item, types.GeneratorType):
                self.queue.put(item)
        return filter(None, results)

    def update_results(self, gt):
        for result in iter_iterable(gt.wait()):
            if result is None:
                continue

            if isinstance(result, self.ScrapelItems):
                nt = collections.namedtuple('Result', result.keys())
                result = nt(**result)
            try:
                hash(result)
            except TypeError:
                continue

            # update it finally
            self.results.update(result)


class FakeWorker(FunctionGetMixin):
    @property
    def service(self):
        return

    def stop(self, *args, **kwargs):
        pass
