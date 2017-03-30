from __future__ import unicode_literals, print_function, absolute_import, division

from collections import defaultdict

from nameko.extensions import ProviderCollector, SharedExtension
from nameko.utils import SpawningProxy

__author__ = 'Fill Q'
__all__ = ['ScrapelEventsCollector']


class ScrapelEventsCollector(ProviderCollector, SharedExtension):
    _providers_by_type = defaultdict(set)

    def register_provider(self, provider):
        super(ScrapelEventsCollector, self).register_provider(provider)
        if not hasattr(provider, 'provider_type'):
            return
        self._providers_by_type[provider.provider_type].add(provider)

    def unregister_provider(self, provider):
        super(ScrapelEventsCollector, self).unregister_provider(provider)
        if not hasattr(provider, 'provider_type'):
            return
        if provider in self._providers_by_type[provider.provider_type]:
            self._providers_by_type[provider.provider_type].remove(provider)

    def on_start(self, worker):
        SpawningProxy(self._providers_by_type['on_start']).call(worker=worker, jid=worker.jid)

    def on_stop(self, worker, results):
        SpawningProxy(self._providers_by_type['on_stop']).call(worker=worker, results=results, jid=worker.jid)

    def pipeline(self, worker, item):
        new_item = item
        for provider in self._providers_by_type['pipeline']:
            new_item = provider.call(worker=worker, item=new_item, settings=worker.settings)
            if new_item is None:
                return
        return new_item

    def start_requests(self, worker):
        return SpawningProxy(self._providers_by_type['start_requests']).call(worker=worker, jid=worker.jid)
