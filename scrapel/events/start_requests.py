from __future__ import unicode_literals, print_function, absolute_import, division

from .base import ScrapelEventsEntrypointBase

__author__ = 'Fill Q'
__all__ = ['start_requests']


class ScrapelStartRequestsEvent(ScrapelEventsEntrypointBase):
    provider_type = 'start_requests'


start_requests = ScrapelStartRequestsEvent.decorator
