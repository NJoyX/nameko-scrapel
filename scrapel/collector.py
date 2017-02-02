from nameko.extensions import ProviderCollector, SharedExtension


class ScrapelMiddlewareCollector(ProviderCollector, SharedExtension):
    download_requests_middlewaries = []

    def start(self):
        # print dir(self), self.sharing_key
        # print self.container, self._providers
        pass

    def process_middleware(self, request, job_id, queue):
        print 'Processing', self._providers, request