from __future__ import unicode_literals, print_function, absolute_import

import collections
import uuid
import weakref
from functools import partial

from nameko.constants import DEFAULT_MAX_WORKERS, MAX_WORKERS_CONFIG_KEY
from nameko.extensions import DependencyProvider

from .middlewares import (
    RequestMiddleware,
    ResponseMiddleware,
    ExceptionMiddleware,
    SpiderInputMiddleware,
    SpiderOutputMiddleware,
    SpiderExceptionMiddleware
)
from .request import Request
from .transport import BaseTransport, Urllib3Transport
from .utils import maybe_iterable
from .worker import ScrapelWorker

__author__ = 'Fill Q'


class Scrapel(DependencyProvider):
    worker = None

    request_middleware = RequestMiddleware.decorator
    response_middleware = ResponseMiddleware.decorator
    exception_middleware = ExceptionMiddleware.decorator
    spider_input_middleware = SpiderInputMiddleware.decorator
    spider_output_middleware = SpiderOutputMiddleware.decorator
    spider_exception_middleware = SpiderExceptionMiddleware.decorator

    _functions = weakref.WeakValueDictionary()
    _functions.setdefault(
        'start_requests',
        lambda self, url=None: map(lambda u: Request(u, callback=self.null), maybe_iterable(url))
    )
    _functions.setdefault('pipelines', weakref.WeakSet())

    def __init__(self, allowed_domains, concurrency=DEFAULT_MAX_WORKERS, transport=Urllib3Transport):
        self.allowed_domains = allowed_domains
        self.transport = transport if issubclass(transport, BaseTransport) else Urllib3Transport
        self.concurrency = concurrency

    def setup(self):
        if not self.concurrency:
            self.concurrency = self.container.config.get(MAX_WORKERS_CONFIG_KEY, DEFAULT_MAX_WORKERS)
        self.worker = ScrapelWorker(
            max_workers=self.concurrency,
            start_requests_func=self._start_requests,
            transport=self.transport
        )

    def get_dependency(self, worker_ctx):
        self.worker.setup(context=worker_ctx)
        return collections.namedtuple('Scrapel', 'start stop free config settings')(
            start=partial(self._start_process, self.worker),
            stop=self.worker.stop,
            free=self.worker.free,
            config=self.worker.config,
            settings=self.worker.settings
        )

    def _start_process(self, worker, job_id=None):
        if job_id is None:
            job_id = uuid.uuid4().hex

        if not worker.free:
            # worker.pool.waitall()
            # return eventlet.with_timeout(3, self._start_process, worker, job_id, timeout_value="")
            raise Exception('No free slots available')

        gt = self.container.spawn_managed_thread(
            partial(worker.run, job_id),
            identifier='<Scrapel Worker with JobID: {} at {}>'.format(job_id, id(worker))
        )
        # @TODO link operation
        gt.link(lambda result: None)  # print(result.wait(), 'Finished'))
        return job_id

    def null(self, response):
        pass

    # Default methods
    def start(self):
        return super(Scrapel, self).start()

    def stop(self):
        self.worker.stop()
        return super(Scrapel, self).stop()

    def kill(self):
        self.worker.stop()
        return super(Scrapel, self).kill()

    # Custom functions
    _on_start = property(lambda self: self._functions.get('on_start'))
    on_start = lambda self, f: self._functions.setdefault('on_start', f)

    _on_stop = property(lambda self: self._functions.get('on_stop'))
    on_stop = lambda self, f: self._functions.setdefault('on_stop', f)

    _pipeline = property(lambda self: self._functions.get('pipelines'))
    pipeline = lambda self, f: self._functions['pipelines'].add(f)

    _start_requests = property(lambda self: self._functions.get('start_requests'))
    start_requests = lambda self, f: self._functions.setdefault('start_requests', f)
