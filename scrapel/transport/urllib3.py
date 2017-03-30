from __future__ import unicode_literals, print_function, absolute_import

import hashlib

try:
    import OpenSSL

    from urllib3.contrib import pyopenssl

    pyopenssl.inject_into_urllib3()
except ImportError:
    OpenSSL = pyopenssl = None

try:
    import certifi
    import cryptography

    SECURE = True
except ImportError:
    certifi = cryptography = None
    SECURE = False

try:
    from urllib3.contrib.socks import SOCKSProxyManager
except ImportError:
    SOCKSProxyManager = None

import six
import urllib3
import weakref
from ssl import CERT_REQUIRED
from scrapel.http.responsetypes import responsetypes
from urllib3.util import parse_url
from w3lib.util import to_bytes

from .base import BaseTransport

__author__ = 'Fill Q'

RETRY_POLICY = {
    'default': {'total': 3},
    'long': {'connect': 60, 'read': 30},
    'quick': {'connect': 7, 'read': 5}
}


class Urllib3Transport(BaseTransport):
    pool_type = {
        None: urllib3.PoolManager,
        'http': urllib3.ProxyManager,
        'https': urllib3.ProxyManager,
        'socks': SOCKSProxyManager or urllib3.PoolManager,
        'socks4': SOCKSProxyManager or urllib3.PoolManager,
        'socks5': SOCKSProxyManager or urllib3.PoolManager
    }

    def __init__(self, *args, **kwargs):
        super(Urllib3Transport, self).__init__(*args, **kwargs)
        self.pool = weakref.WeakValueDictionary()

    def make_response(self, request):
        request_kwargs = {}
        if isinstance(request.body, dict) and request.method == 'POST':
            request_kwargs['fields'] = request.body
        else:
            request_kwargs['body'] = request.body

        http = self.build_http(request=request)
        headers = request.headers.to_unicode_dict()
        result = http.request(request.method, url=request.url, headers=headers, **request_kwargs)
        try:
            body = to_bytes(result.data.decode(request.encoding))
        except Exception:
            body = to_bytes(request.data)

        response_cls = responsetypes.from_args(
            headers=result.headers,
            url=request.url,
            body=body
        )
        return response_cls(
            url=request.url,
            status=result.status,
            headers=result.headers,
            body=body,
            request=request
        )

    get = (
        lambda self, name, request, default=None:
        request.meta.get(name, self.worker.config.get(name.upper(), self.settings.get(name, default)))
    )
    proxy = (lambda self, request: self.get('proxy', request=request) or '')
    is_proxy = (lambda self, request: (
        isinstance(self.proxy(request=request), (six.text_type, six.binary_type) + six.string_types)
        and (self.proxy(request).startswith('http') or self.proxy(request).startswith('socks'))
    ))
    proxy_key = (lambda self, request: hashlib.md5(self.proxy(request)).hexdigest() if self.is_proxy(request) else '')

    def build_http(self, request):
        proxy_key = self.proxy_key(request)
        if proxy_key in self.pool:
            return self.pool.get(proxy_key)

        kwargs = self.build_kwargs(request=request)
        _type = self.build_type(request=request)
        self.pool[proxy_key] = instance = _type(**kwargs) if callable(_type) else urllib3.PoolManager(**kwargs)
        return instance

    def build_kwargs(self, request):
        kwargs = {}
        retries = self.get('retries', request=request)
        if isinstance(retries, (int, bool)):
            kwargs['retries'] = retries
        else:
            retry_policy = RETRY_POLICY.get(self.get('retry_policy', request=request, default='default'), {})
            retry_raise_errors = bool(self.get('retry_raise_errors', request=request, default=True))
            if not retry_raise_errors:
                retry_policy.update(dict(raise_on_redirect=False, raise_on_status=False))
            retry_policy['connect'] = self.get('retry_connect', request=request)
            retry_policy['read'] = self.get('retry_read', request=request)
            retry_policy['redirect'] = self.get('retry_redirect', request=request)
            status_forcelist = self.get('status_forcelist', request=request)
            if isinstance(status_forcelist, (list, tuple)):
                retry_policy['status_forcelist'] = tuple(status_forcelist)
            kwargs['retries'] = urllib3.Retry(**retry_policy)

        timeout = self.get('timeout', request=request)
        if isinstance(timeout, float):
            kwargs['timeout'] = timeout
        else:
            timeout_kw = {
                'read': self.get('timeout_read', request=request, default=urllib3.Timeout.DEFAULT_TIMEOUT),
                'connect': self.get('timeout_connect', request=request, default=urllib3.Timeout.DEFAULT_TIMEOUT)
            }
            kwargs['timeout'] = urllib3.Timeout(**timeout_kw)

        kwargs['num_pools'] = self.get('num_pools', request=request, default=10)
        kwargs['block'] = True

        if SECURE:
            kwargs['cert_reqs'] = CERT_REQUIRED
            kwargs['ca_certs'] = certifi.where()

        if self.is_proxy(request=request):
            kwargs.update(self.build_proxy(request=request))
            kwargs['num_pools'] = 2
        return kwargs

    def build_proxy(self, request):
        kwargs = {}
        proxy = self.proxy(request)
        is_socks_proxy = proxy.startswith('socks')

        urlparsed = parse_url(proxy)
        auth = urlparsed.auth or ''
        kwargs['proxy_url'] = self._build_parsed(urlparsed=urlparsed)
        kwargs['proxy_headers'] = urllib3.make_headers(proxy_basic_auth=auth) if auth else None
        if is_socks_proxy:
            kwargs.pop('proxy_headers')
            auth_splitted = filter(None, auth.split(':'))
            kwargs['username'], kwargs['password'] = auth_splitted + [None] * (2 - len(auth_splitted))

        if SOCKSProxyManager is None and is_socks_proxy:
            kwargs.pop('proxy_url', None)
            kwargs.pop('username', None)
            kwargs.pop('password', None)
        return kwargs

    def build_type(self, request):
        _type = parse_url(self.proxy(request=request)).scheme
        return self.pool_type.get(_type) or urllib3.PoolManager

    @staticmethod
    def _build_parsed(urlparsed, auth=False):
        path = '{0.scheme}://'
        if urlparsed.auth is not None and auth:
            path += '{0.auth}@'
        path += '{0.host}'
        if urlparsed.port is not None:
            path += ':{0.port}'
        path += '{0.path}'
        if urlparsed.query is not None:
            path += '?{0.query}'
        if urlparsed.fragment is not None:
            path += '#{0.fragment}'
        return path.format(urlparsed)
