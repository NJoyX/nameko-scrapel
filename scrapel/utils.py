from eventlet.support import six


def maybe_iterable(items):
    if isinstance(items, (six.text_type, six.binary_type) + six.string_types + six.integer_types):
        return iter([items])
    elif isinstance(items, (list, tuple)):
        return items
    elif hasattr(items, '__iter__'):
        return items
    return iter([items])
