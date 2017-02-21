from __future__ import unicode_literals, print_function, absolute_import

import weakref

__author__ = 'Fill Q'
__all__ = ['handler', 'getter']


class ScrapelHandler(object):
    _on_start = None
    _on_stop = None
    _pipeline = weakref.WeakSet()
    _start_requests = None

    def on_start(self, f):
        self._on_start = weakref.ref(f)
        return f

    def on_stop(self, f):
        self._on_stop = weakref.ref(f)
        return f

    def pipeline(self, f):
        self._pipeline.add(f)
        return f

    def start_requests(self, f):
        self._start_requests = weakref.ref(f)
        return f


handler = ScrapelHandler()


class ScrapelHandlerGetter(object):
    def __getattribute__(self, name):
        try:
            return handler.__dict__['_{}'.format(name)]()
        except (KeyError, ReferenceError):
            return lambda *args, **kwargs: None


getter = ScrapelHandlerGetter()
