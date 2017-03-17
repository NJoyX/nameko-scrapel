from __future__ import unicode_literals, print_function, absolute_import

import weakref
from functools import partial
from .python import maybe_iterable

__author__ = 'Fill Q'
__all__ = ['FunctionGetMixin', 'FunctionSetMixin']


class FunctionRegistry(object):
    _on_start = None
    _on_stop = None
    _pipeline = weakref.WeakSet()
    _start_requests = None

    def on_start(self, f):
        if callable(f):
            self._on_start = weakref.ref(f)
        return f

    def on_stop(self, f):
        if callable(f):
            self._on_stop = weakref.ref(f)
        return f

    def pipeline(self, f):
        if callable(f):
            self._pipeline.add(f)
        return f

    def start_requests(self, f):
        if callable(f):
            self._start_requests = weakref.ref(f)
        return f


class FunctionRegistryGetter(object):
    def __getattribute__(self, name):
        try:
            return _registry_setter.__dict__['_{}'.format(name)]()
        except (KeyError, ReferenceError, TypeError):
            return lambda *args, **kwargs: None


_registry_setter = FunctionRegistry()
_registry_getter = FunctionRegistryGetter()


class FunctionSetMixin(object):
    on_start = _registry_setter.on_start
    on_stop = _registry_setter.on_stop
    pipeline = _registry_setter.pipeline
    start_requests = _registry_setter.start_requests


class FunctionGetMixin(object):
    on_start = property(lambda self: partial(_registry_getter.on_start, self.service))
    on_stop = property(lambda self: partial(_registry_getter.on_stop, self.service))
    start_requests = property(lambda self: partial(_registry_getter.start_requests, self.service))

    @property
    def pipeline(self):
        return set(map(lambda p: partial(p, self.service), maybe_iterable(_registry_setter._pipeline)))

    @property
    def service(self):
        raise NotImplementedError
