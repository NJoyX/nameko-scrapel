class BaseTransport(object):
    def __init__(self, worker, settings):
        self.worker = worker
        self.settings = settings

    def make_response(self, request, settings):
        raise NotImplementedError
