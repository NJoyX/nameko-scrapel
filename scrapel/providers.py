from __future__ import unicode_literals, print_function, absolute_import

import weakref
from functools import partial

import six
from nameko.extensions import DependencyProvider
from nameko.utils import SpawningProxy

from .constants import JOBID
from .exceptions import NoFreeSlotsAvailable
from .decorators import (
    request_middleware,
    response_middleware,
    exception_middleware,
    spider_input_middleware,
    spider_output_middleware,
    spider_exception_middleware
)
from .settings import Settings
from .transport import BaseTransport, Urllib3Transport
from .utils import try_int, FunctionSetMixin
from .worker import ScrapelWorker, FakeWorker

__author__ = 'Fill Q'


DEFAULT_MAX_WORKERS = 30


class Scrapel(FunctionSetMixin, DependencyProvider):
    def __init__(self, allowed_domains, concurrency=None, transport_cls=Urllib3Transport):
        assert isinstance(allowed_domains, (list, tuple)), 'Incorrect format of allowed_domains'
        self.allowed_domains = filter(six.text_type, allowed_domains)
        assert self.allowed_domains, 'Empty Allowed Domains list'
        self.transport_cls = transport_cls if issubclass(transport_cls, BaseTransport) else Urllib3Transport
        self.concurrency = try_int(concurrency, default=DEFAULT_MAX_WORKERS)
        self.jobs = weakref.WeakValueDictionary()

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
            transport_cls=self.transport_cls,
            allowed_domains=self.allowed_domains,
            **settings
        )

    def stop_worker(self, job_id):
        SpawningProxy([self.jobs.pop(job_id, FakeWorker())]).stop()

    def start_worker(self, context, job_id=None, **settings):
        job_id = six.text_type(job_id or context.call_id)

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
    request_middleware = request_middleware
    response_middleware = response_middleware
    exception_middleware = exception_middleware
    spider_input_middleware = spider_input_middleware
    spider_output_middleware = spider_output_middleware
    spider_exception_middleware = spider_exception_middleware
