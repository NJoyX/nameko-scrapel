from __future__ import unicode_literals, print_function, absolute_import

from .download import (
    ChunkedTransferMiddleware,
    CookiesMiddleware,
    DecompressionMiddleware,
    DefaultHeadersMiddleware,
    HttpCompressionMiddleware,
    RedirectMiddleware,
    MetaRefreshMiddleware,
    UserAgentMiddleware
)
from .spider import (
    DepthMiddleware,
    HttpErrorMiddleware,
    OffsiteMiddleware,
    RefererMiddleware,
    UrlLengthMiddleware
)

__author__ = 'Fill Q'
__all__ = [
    'ContributedMiddlewares'
]


class ContributedMiddlewares(
    # download middlewares
    ChunkedTransferMiddleware,
    CookiesMiddleware,
    DecompressionMiddleware,
    DefaultHeadersMiddleware,
    HttpCompressionMiddleware,
    RedirectMiddleware,
    MetaRefreshMiddleware,
    UserAgentMiddleware,

    # spider middlewares
    DepthMiddleware,
    HttpErrorMiddleware,
    OffsiteMiddleware,
    RefererMiddleware,
    UrlLengthMiddleware
):  # fin
    pass
