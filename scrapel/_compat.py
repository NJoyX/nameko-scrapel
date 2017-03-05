from functools import partial

from eventlet.support.six import PY2

if PY2:
    class partialmethod(partial):
        def __get__(self, instance, owner):
            if instance is None:
                return self
            return partial(self.func, instance,
                           *(self.args or ()), **(self.keywords or {}))
else:
    # noinspection PyUnresolvedReferences
    from functools import partialmethod
