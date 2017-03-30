from __future__ import unicode_literals, print_function, absolute_import
from scrapel.exceptions import ItemDropped
from .base import ScrapelEventsEntrypointBase

__author__ = 'Fill Q'
__all__ = ['pipeline']


class ScrapelPipeline(ScrapelEventsEntrypointBase):
    provider_type = 'pipeline'

    def process_result(self, result, item, settings):
        return result if isinstance(result, type(item)) else item

    def process_exception(self, exc, item, settings):
        if isinstance(exc, ItemDropped):
            return None
        return item

pipeline = ScrapelPipeline.decorator
