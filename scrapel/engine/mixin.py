from __future__ import unicode_literals, print_function, absolute_import

from scrapel.utils import maybe_iterable

__author__ = 'Fill Q'
__all__ = ['ScrapelProvidersMixin']


class ScrapelProvidersMixin(object):
    _sort_key = (lambda self, p: p.priority or p.__class__.__name__)

    def _providers_by_method(self, method, key=None, sort=True, reverse=False):
        if key is None:
            key = self._sort_key

        providers = filter(lambda p: p.method == method, self.providers)
        if sort:
            kwargs = dict(key=key, reverse=True if reverse else False)
            return sorted(providers, **kwargs)
        return providers

    @staticmethod
    def filter_by_dispatch_uid(providers, dispatch_uid):
        return filter(lambda p: dispatch_uid == getattr(p, 'dispatch_uid', ''), providers or set())

    def next_in_chain(self, providers, dispatch_uid):
        current_provider = self.filter_by_dispatch_uid(providers, dispatch_uid=dispatch_uid)
        return providers[(providers.index(current_provider) + 1):]

    @property
    def providers(self):
        raise NotImplementedError

    # Process Helpers
    @staticmethod
    def pre_process_one(gt):
        try:
            return maybe_iterable(gt.wait()).next()
        except StopIteration:
            pass
        return

    @staticmethod
    def pre_process_many(gt):
        return maybe_iterable(gt.wait())

    @staticmethod
    def filter_result(gt, classes):
        results = maybe_iterable(gt.wait())
        return filter(lambda r: isinstance(r, classes), results)
