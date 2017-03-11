from __future__ import unicode_literals, print_function, absolute_import

try:
    import OpenSSL

    from urllib3.contrib import pyopenssl

    pyopenssl.inject_into_urllib3()
except ImportError:
    OpenSSL = None
    pyopenssl = None

try:
    import certifi
    import cryptography

    SECURE = True
except ImportError:
    certifi = None
    cryptography = None
    SECURE = False

try:
    from urllib3.contrib.socks import SOCKSProxyManager
except ImportError:
    SOCKSProxyManager = None

import six
import urllib3
import weakref
from scrapel.utils.python import memoizemethod_noargs
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
        'proxy': urllib3.ProxyManager,
        'socks': SOCKSProxyManager or urllib3.PoolManager
    }

    def __init__(self, *args, **kwargs):
        super(Urllib3Transport, self).__init__(*args, **kwargs)
        self.pool = weakref.WeakValueDictionary()

    proxy = property(lambda self: self.get('proxy'))
    is_proxy = property(lambda self: (
        isinstance(self.proxy, (six.text_type, six.binary_type) + six.string_types)
        and (self.proxy.startswith('http') or self.proxy.startswith('socks'))
    ))

    @property
    def http(self):
        pooled = self.pool.get(self.proxy)
        if pooled:
            return pooled

        kwargs = self.collected_kwargs()
        _type = None
        if self.is_proxy:
            _type = 'proxy' if self.proxy.startswith('http') else 'socks'
            kwargs['num_pools'] = 2
        self.pool[self.proxy] = instance = self.pool_type.get(_type)(**kwargs)
        return instance

    def make_response(self, request):
        request_kwargs = {}
        if isinstance(request.body, dict) and request.method == 'POST':
            request_kwargs['fields'] = request.body
        else:
            request_kwargs['body'] = request.body

        # @TODO add Cookies
        headers = request.headers.to_unicode_dict()
        result = self.http.request(request.method, url=request.url, headers=headers, **request_kwargs)
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

    @memoizemethod_noargs
    def collected_kwargs(self):
        kwargs = {}
        retries = self.get('retries')
        if isinstance(retries, (int, bool)):
            kwargs['retries'] = retries
        else:
            retry_policy = RETRY_POLICY.get(self.get('retry_policy', 'default'), {})
            retry_raise_errors = self.get('retry_raise_errors', True)
            if not retry_raise_errors:
                retry_policy.update(dict(raise_on_redirect=False, raise_on_status=False))
            retry_policy['connect'] = self.get('retry_connect')
            retry_policy['read'] = self.get('retry_read')
            retry_policy['redirect'] = self.get('retry_redirect')
            status_forcelist = self.get('status_forcelist')
            if isinstance(status_forcelist, (list, tuple)):
                retry_policy['status_forcelist'] = tuple(status_forcelist)
            kwargs['retries'] = urllib3.Retry(**retry_policy)

        timeout = self.get('timeout')
        if isinstance(timeout, float):
            kwargs['timeout'] = timeout
        else:
            timeout_kw = {'read': self.get('timeout_read', urllib3.Timeout.DEFAULT_TIMEOUT),
                          'connect': self.get('timeout_connect', urllib3.Timeout.DEFAULT_TIMEOUT)}
            kwargs['timeout'] = urllib3.Timeout(**timeout_kw)

        kwargs['num_pools'] = self.get('num_pools', 10)
        kwargs['block'] = True

        if SECURE:
            kwargs['cert_reqs'] = 'CERT_REQUIRED'
            kwargs['ca_certs'] = certifi.where()

        if self.is_proxy:
            auth = parse_url(self.proxy).auth
            kwargs['proxy_url'] = self.proxy
            kwargs['proxy_headers'] = urllib3.make_headers(proxy_basic_auth=auth) if auth else None
            if self.proxy.startswith('socks'):
                kwargs.pop('proxy_headers')
                auth_splitted = auth.split(':')
                kwargs['username'] = auth_splitted[0] if len(auth_splitted) > 0 else None
                kwargs['password'] = auth_splitted[1] if len(auth_splitted) > 1 else None

        if SOCKSProxyManager is None:
            kwargs.pop('proxy_url', None)
            kwargs.pop('username', None)
            kwargs.pop('password', None)

        return kwargs

    def get(self, name, default=None):
        return self.worker.config.get(name, self.settings.get(name.upper(), default))
