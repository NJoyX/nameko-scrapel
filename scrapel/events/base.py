from __future__ import unicode_literals, print_function, absolute_import, division

from nameko.exceptions import IncorrectSignature
from nameko.extensions import Entrypoint
from .collector import ScrapelEventsCollector

__author__ = 'Fill Q'
__all__ = ['ScrapelEventsEntrypointBase']


class ScrapelEventsEntrypointBase(Entrypoint):
    collector = ScrapelEventsCollector()
    provider_type = None

    def start(self):
        self.collector.register_provider(self)

    def stop(self):
        self.collector.unregister_provider(self)
        super(ScrapelEventsEntrypointBase, self).stop()

    # @TODO move processing into eventlet.events
    def process_result(self, result, *args, **kwargs):
        return result

    # @TODO move processing into eventlet.events
    def process_exception(self, exc, *args, **kwargs):
        return exc

    def call(self, worker, *args, **kwargs):
        try:
            self.check_signature(args, kwargs)
            service_cls = self.container.service_cls
            fn = getattr(service_cls, self.method_name)
            result = fn(worker.context.service, *args, **kwargs)
            return self.process_result(result=result, *args, **kwargs)
        except IncorrectSignature:
            pass
        except Exception as exc:
            return self.process_exception(exc=exc, *args, **kwargs)
