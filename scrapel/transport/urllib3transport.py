from __future__ import unicode_literals, print_function, absolute_import

import urllib3
from lazy_object_proxy.utils import cached_property
from w3lib.util import to_bytes

from .base import BaseTransport

try:
    import OpenSSL

    import urllib3.contrib.pyopenssl

    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass

try:
    import certifi
    import cryptography

    SECURE = True
except ImportError:
    SECURE = False

from scrapel.http.responsetypes import responsetypes

__author__ = 'Fill Q'


RETRY_POLICY = {
    'default': {'total': 3},
    'long': {'connect': 60, 'read': 30},
    'quick': {'connect': 7, 'read': 5}
}


class Urllib3Transport(BaseTransport):
    cls = urllib3.PoolManager
    proxy_cls = urllib3.ProxyManager

    def __init__(self, *args, **kwargs):
        super(Urllib3Transport, self).__init__(*args, **kwargs)

    def get(self, name, default=None):
        return self.worker.config.get(name, self.settings.get(name.upper(), default))

    def make_response(self, request):
        _proxy = request.meta.get('proxy', self.get('proxy', ''))
        cls = self.cls
        if _proxy and _proxy.startswith('http'):
            cls = self.proxy_cls
        # @TODO Socks Proxy

        urlopen_kwargs = self.collected_kwargs
        if SECURE:
            urlopen_kwargs['cert_reqs'] = 'CERT_REQUIRED'
            urlopen_kwargs['ca_certs'] = certifi.where()
        http = cls(**urlopen_kwargs)
        request_kwargs = {}
        if isinstance(request.body, dict) and request.method == 'POST':
            request_kwargs['fields'] = request.body
        else:
            request_kwargs['body'] = request.body

        # @TODO add Cookies
        headers = request.headers.to_unicode_dict()
        result = http.request(request.method, url=request.url, headers=headers, **request_kwargs)
        try:
            body = to_bytes(result.data.decode(request.encoding))
        except Exception as exc:
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

    @cached_property
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
        return kwargs
