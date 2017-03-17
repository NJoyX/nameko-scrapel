from __future__ import unicode_literals, print_function, absolute_import

import weakref
from functools import wraps

from eventlet.support import six

__author__ = 'Fill Q'
__all__ = ['maybe_iterable', 'iter_iterable', 'get_callable', 'try_int']


def maybe_iterable(items):
    if isinstance(items, (six.text_type, six.binary_type) + six.string_types + six.integer_types):
        items = [items]
    elif items is None:
        items = []
    elif isinstance(items, dict):
        items = [items]
    elif isinstance(items, (list, tuple)) or hasattr(items, '__iter__'):
        pass
    else:
        items = [items]
    return iter(items)


def iter_iterable(items):
    result = maybe_iterable(items)
    while True:
        try:
            yield next(result)
        except StopIteration:
            break
        except:
            break


def get_callable(obj, name):
    _callable = getattr(obj, name, None)
    if callable(_callable):
        return _callable
    return


def try_int(integer, default=None):
    try:
        return int(integer)
    except (TypeError, ValueError):
        return default


_BINARYCHARS = {six.b(chr(i)) for i in range(32)} - {b"\0", b"\t", b"\n", b"\r"}
_BINARYCHARS |= {ord(ch) for ch in _BINARYCHARS}


def binary_is_text(data):
    """ Returns `True` if the given ``data`` argument (a ``bytes`` object)
    does not contain unprintable control characters.
    """
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes, got '%s'" % type(data).__name__)
    return all(c not in _BINARYCHARS for c in data)


def is_listlike(x):
    """
    >>> is_listlike("foo")
    False
    >>> is_listlike(5)
    False
    >>> is_listlike(b"foo")
    False
    >>> is_listlike([b"foo"])
    True
    >>> is_listlike((b"foo",))
    True
    >>> is_listlike({})
    True
    >>> is_listlike(set())
    True
    >>> is_listlike((x for x in range(3)))
    True
    >>> is_listlike(six.moves.xrange(5))
    True
    """
    return hasattr(x, "__iter__") and not isinstance(x, (six.text_type, bytes))


def memoizemethod_noargs(method):
    """Decorator to cache the result of a method (without arguments) using a
    weak reference to its object
    """
    cache = weakref.WeakKeyDictionary()

    @wraps(method)
    def new_method(self, *args, **kwargs):
        if self not in cache:
            cache[self] = method(self, *args, **kwargs)
        return cache[self]

    return new_method
