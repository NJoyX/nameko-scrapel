from functools import partial

from nameko.extensions import ProviderCollector, SharedExtension
from .constants import DOWNLOAD_METHOD, SPIDER_METHOD, JOBID
from .utils import get_callable
from .request import Request
from .response import Response


class ScrapelCollector(ProviderCollector, SharedExtension):
    @property
    def download_middlewares(self):
        return filter(lambda p: getattr(p, 'method', None) in (DOWNLOAD_METHOD,), self._providers)

    @property
    def spider_middlewares(self):
        return filter(lambda p: getattr(p, 'method', None) in (SPIDER_METHOD,), self._providers)

    @staticmethod
    def job_id(settings):
        return settings.get(JOBID)

    def process_request(self, request, transport, worker, settings):
        job_id = self.job_id(settings)
        post_process = partial(self.post_process, worker)
        for dlm in self.download_middlewares:
            _callback = get_callable(dlm, 'process')
            if _callback is None:
                continue
            gt = worker.spawn(_callback, request, transport, settings, job_id, worker.context)
            gt.link(lambda result: post_process(result.wait()))

    @staticmethod
    def post_process(worker, result):
        if isinstance(result, (Request, Response)):  # , Item)):
            worker.queue.put(result)
        elif isinstance(result, Exception):
            print(result)

    def process_response(self, response, worker, settings):
        job_id = self.job_id(settings)
        request = response.request
        post_process = partial(self.post_process, worker)
        for spm in self.spider_middlewares:
            _callback = get_callable(spm, 'process')
            if _callback is None:
                continue
            gt = worker.spawn(_callback, response, request, settings, job_id, worker.context)
            gt.link(lambda result: post_process(result.wait()))

    def process_item(self, item, settings):
        job_id = self.job_id(settings)
