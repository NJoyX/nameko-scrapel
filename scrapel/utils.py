from eventlet.support import six

from .constants import MIDDLEWARE_METHODS


def maybe_iterable(items):
    if isinstance(items, (six.text_type, six.binary_type) + six.string_types + six.integer_types):
        items = [items]
    elif items is None:
        items = []
    elif isinstance(items, (list, tuple)) or hasattr(items, '__iter__'):
        pass
    else:
        items = [items]
    return iter(items)


def valid_providers(providers):
    return filter(
        lambda p: getattr(p, 'method', None) in MIDDLEWARE_METHODS and getattr(p, 'priority', None),
        maybe_iterable(providers)
    )


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
