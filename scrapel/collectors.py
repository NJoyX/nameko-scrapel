from functools import partial

from nameko.extensions import ProviderCollector, SharedExtension
from .constants import DOWNLOAD_METHOD, SPIDER_METHOD, JOBID
from .utils import get_callable
from .request import Request
from .response import Response


class ScrapelCollector(ProviderCollector, SharedExtension):
    def start(self):
        # print dir(self), self.sharing_key
        # print self.container, self._providers
        pass

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
        pprocess = partial(self.post_process, worker)
        for dlmiddleware in self.download_middlewares:
            if get_callable(dlmiddleware, 'process'):
                gt = worker.spawn(dlmiddleware.process, request, transport, settings, job_id)
                gt.link(lambda result: pprocess(result.wait()))

    @staticmethod
    def post_process(worker, result):
        if isinstance(result, (Request, Response)):  # , Item)):
            worker.queue.put(result)
        elif isinstance(result, Exception):
            print(result)

    def process_response(self, response, worker, settings):
        job_id = self.job_id(settings)
        request = response.request
        pprocess = partial(self.post_process, worker)
        for spmiddleware in self.spider_middlewares:
            if get_callable(spmiddleware, 'process'):
                gt = worker.spawn(spmiddleware.process, response, request, settings, job_id)
                gt.link(lambda result: pprocess(result.wait()))

    def process_item(self, item, settings):
        job_id = self.job_id(settings)
