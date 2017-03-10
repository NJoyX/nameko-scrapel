class BaseTransport(object):
    def __init__(self, worker, settings):
        self.settings = settings
        self.worker = worker

    def make_response(self, request):
        raise NotImplementedError
