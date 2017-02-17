from __future__ import unicode_literals, print_function, absolute_import

import uuid
import weakref
from functools import partial

from nameko.constants import DEFAULT_MAX_WORKERS, MAX_WORKERS_CONFIG_KEY
from nameko.extensions import DependencyProvider

from .constants import (
    MIDDLEWARE_REQUEST_METHOD,
    MIDDLEWARE_RESPONSE_METHOD,
    MIDDLEWARE_INPUT_METHOD,
    MIDDLEWARE_OUTPUT_METHOD,
    MIDDLEWARE_EXCEPTION_METHOD,
    JOBID
)
from .middleware import (
    RequestMiddleware,
    ResponseMiddleware,
    ExceptionMiddleware,
    SpiderInputMiddleware,
    SpiderOutputMiddleware,
    SpiderExceptionMiddleware
)
from .request import Request
from .transport import BaseTransport, Urllib3Transport
from .utils import maybe_iterable, try_int
from .worker import ScrapelWorker
from .exceptions import NoFreeSlotsAvailable
from .settings import Settings

__author__ = 'Fill Q'


class Scrapel(DependencyProvider):
    request_middleware = partial(RequestMiddleware.decorator, method=MIDDLEWARE_REQUEST_METHOD)
    response_middleware = partial(ResponseMiddleware.decorator, method=MIDDLEWARE_RESPONSE_METHOD)
    exception_middleware = partial(ExceptionMiddleware.decorator, method=MIDDLEWARE_EXCEPTION_METHOD)
    spider_input_middleware = partial(SpiderInputMiddleware.decorator, method=MIDDLEWARE_INPUT_METHOD)
    spider_output_middleware = partial(SpiderOutputMiddleware.decorator, method=MIDDLEWARE_OUTPUT_METHOD)
    spider_exception_middleware = partial(SpiderExceptionMiddleware.decorator, method=MIDDLEWARE_EXCEPTION_METHOD)

    _functions = weakref.WeakValueDictionary()
    _functions.setdefault(
        'start_requests',
        lambda self, url=None: map(lambda u: Request(u, callback=self.null), maybe_iterable(url))
    )
    _functions.setdefault('pipelines', weakref.WeakSet())

    jobs = weakref.WeakValueDictionary()

    def null(self, response):
        pass

    def __init__(self, allowed_domains, concurrency=DEFAULT_MAX_WORKERS, transport=Urllib3Transport):
        self.allowed_domains = allowed_domains
        self.transport = transport if issubclass(transport, BaseTransport) else Urllib3Transport
        self.concurrency = try_int(concurrency, default=concurrency)

    def setup(self):
        if self.concurrency is None:
            self.concurrency = try_int(self.container.config.get(MAX_WORKERS_CONFIG_KEY, DEFAULT_MAX_WORKERS))

    def get_dependency(self, worker_ctx):
        return type(str('Scrapel'), (), dict(
            start=partial(self._start_process, worker_ctx),
            stop=self._stop_worker,
            free=self.free,
            config=self.container.config,
            settings=self._settings
        ))

    def worker_cls(self, context, job_id):
        return ScrapelWorker(
            context=context,
            job_id=job_id,
            start_requests_func=self._start_requests,
            transport=self.transport
        )

    def _start_process(self, context, job_id=None):
        if job_id is None:
            job_id = uuid.uuid4().hex

        if job_id in self.jobs:
            return job_id

        if not self.free:
            raise NoFreeSlotsAvailable('No free slots available')

        worker = self.worker_cls(context=context, job_id=job_id)
        self.jobs[job_id] = worker

        if callable(self._on_start):
            worker.pile(self._on_start, context.service)
        gt = self.container.spawn_managed_thread(
            worker.run,
            identifier='<Scrapel Worker with JobID: {} at {}>'.format(job_id, id(worker))
        )
        if not callable(self._on_stop):
            on_stop = partial(lambda this, gthread, result: print(result.wait()), self, gt)
        else:
            on_stop = partial(self._on_stop, context.service, gt)
        gt.link(lambda result: on_stop(result))
        return job_id

    def _stop_worker(self, job_id):
        if job_id in self.jobs:
            self.jobs[job_id].stop()

    @property
    def free(self):
        return len(filter(lambda j: j.is_running, self.jobs.values())) < self.concurrency

    def _settings(self, job_id):
        return getattr(self.jobs.get(job_id), 'settings', Settings(**{JOBID: job_id}))

    # Default methods
    def start(self):
        return super(Scrapel, self).start()

    def stop(self):
        map(lambda w: w.stop(), self.jobs.values())
        return super(Scrapel, self).stop()

    def kill(self):
        map(lambda w: w.stop(), self.jobs.values())
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
