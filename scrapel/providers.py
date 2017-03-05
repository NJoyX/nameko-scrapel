from __future__ import unicode_literals, print_function, absolute_import

import weakref
from functools import partial

from nameko.constants import DEFAULT_MAX_WORKERS, MAX_WORKERS_CONFIG_KEY
from nameko.extensions import DependencyProvider
from nameko.utils import SpawningProxy

from .constants import JOBID
from .exceptions import NoFreeSlotsAvailable
from .middleware import (
    DownloaderRequestMiddleware,
    DownloaderResponseMiddleware,
    DownloaderExceptionMiddleware,
    SpiderInputMiddleware,
    SpiderOutputMiddleware,
    SpiderExceptionMiddleware
)
from .settings import Settings
from .transport import BaseTransport, Urllib3Transport
from .utils import try_int, FunctionSetMixin
from .worker import ScrapelWorker, FakeWorker

__author__ = 'Fill Q'

CONCURRENCY = int(DEFAULT_MAX_WORKERS / 2)


class Scrapel(FunctionSetMixin, DependencyProvider):
    def __init__(self, allowed_domains, concurrency=CONCURRENCY, transport=Urllib3Transport):
        self.allowed_domains = allowed_domains
        self.transport = transport if issubclass(transport, BaseTransport) else Urllib3Transport
        self.concurrency = try_int(concurrency, default=concurrency)
        self.jobs = weakref.WeakValueDictionary()

    def setup(self):
        if self.concurrency is None:
            self.concurrency = try_int(self.container.config.get(MAX_WORKERS_CONFIG_KEY, DEFAULT_MAX_WORKERS))

    def get_dependency(self, worker_ctx):
        return type(str('Scrapel'), (), dict(
            start=partial(self.start_worker, worker_ctx),
            stop=self.stop_worker,
            free=self.free,
            config=self.container.config,
            settings=self.settings
        ))

    def worker_cls(self, context, job_id, **settings):
        return ScrapelWorker(
            context=context,
            job_id=job_id,
            transport=self.transport,
            **settings
        )

    def stop_worker(self, job_id):
        SpawningProxy([self.jobs.pop(job_id, FakeWorker())]).stop()

    def start_worker(self, context, job_id=None, **settings):
        job_id = job_id or context.call_id

        if job_id in self.jobs:
            return job_id

        if not self.free:
            raise NoFreeSlotsAvailable('No free slots available')

        worker = self.worker_cls(context=context, job_id=job_id, **settings)
        self.jobs[job_id] = worker

        gt = self.container.spawn_managed_thread(
            partial(worker.on_start, jid=job_id),
            identifier='<Scrapel Worker with JobID: {} at {}>'.format(job_id, id(worker))
        )
        gt.link(worker.run)
        gt.link(lambda _, jid: self.jobs.pop(jid, None), job_id)
        return job_id

    @property
    def running(self):
        return filter(lambda j: j.is_running, self.jobs.values())

    @property
    def free(self):
        return len(self.running) < self.concurrency

    def settings(self, job_id):
        return getattr(self.jobs.get(job_id), 'settings', Settings(**{JOBID: job_id}))

    # Default methods
    def start(self):
        return super(Scrapel, self).start()

    def stop(self):
        SpawningProxy(self.running).stop()
        return super(Scrapel, self).stop()

    def kill(self):
        SpawningProxy(self.running).stop()
        return super(Scrapel, self).kill()

    # Entrypoints
    request_middleware = DownloaderRequestMiddleware.decorator
    response_middleware = DownloaderResponseMiddleware.decorator
    exception_middleware = DownloaderExceptionMiddleware.decorator
    spider_input_middleware = SpiderInputMiddleware.decorator
    spider_output_middleware = SpiderOutputMiddleware.decorator
    spider_exception_middleware = SpiderExceptionMiddleware.decorator
