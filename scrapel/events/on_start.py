from __future__ import unicode_literals, print_function, absolute_import, division

from .base import ScrapelEventsEntrypointBase

__author__ = 'Fill Q'
__all__ = ['on_start']


class ScrapelOnStartEvent(ScrapelEventsEntrypointBase):
    provider_type = 'on_start'


on_start = ScrapelOnStartEvent.decorator
