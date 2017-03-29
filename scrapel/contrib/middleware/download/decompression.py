from __future__ import unicode_literals, print_function, absolute_import

import bz2
import gzip
import tarfile
import zipfile
from tempfile import mktemp

import six
from scrapel.http.responsetypes import responsetypes

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

from scrapel.decorators import response_middleware

__author__ = 'Fill Q and Scrapy developers'
__all__ = ['DecompressionMiddleware']

PRIORITY = 570


class DecompressionMiddleware(object):
    """ This middleware tries to recognise and extract the possibly compressed
    responses that may arrive. """
    DECOMPRESSION_ENABLED = False

    def __init__(self):
        self._formats = {
            'tar': self._is_tar,
            'zip': self._is_zip,
            'gz': self._is_gzip,
            'bz2': self._is_bzip2
        }

    @staticmethod
    def _is_tar(response):
        archive = BytesIO(response.body)
        try:
            tar_file = tarfile.open(name=mktemp(), fileobj=archive)
        except tarfile.ReadError:
            return

        body = tar_file.extractfile(tar_file.members[0]).read()
        respcls = responsetypes.from_args(filename=tar_file.members[0].name, body=body)
        return response.replace(body=body, cls=respcls)

    @staticmethod
    def _is_zip(response):
        archive = BytesIO(response.body)
        try:
            zip_file = zipfile.ZipFile(archive)
        except zipfile.BadZipfile:
            return

        namelist = zip_file.namelist()
        body = zip_file.read(namelist[0])
        respcls = responsetypes.from_args(filename=namelist[0], body=body)
        return response.replace(body=body, cls=respcls)

    @staticmethod
    def _is_gzip(response):
        archive = BytesIO(response.body)
        try:
            body = gzip.GzipFile(fileobj=archive).read()
        except IOError:
            return

        respcls = responsetypes.from_args(body=body)
        return response.replace(body=body, cls=respcls)

    @staticmethod
    def _is_bzip2(response):
        try:
            body = bz2.decompress(response.body)
        except IOError:
            return

        respcls = responsetypes.from_args(body=body)
        return response.replace(body=body, cls=respcls)

    @response_middleware(priority=PRIORITY, enabled=DECOMPRESSION_ENABLED)
    def _decompression_process_response(self, request, response, settings):
        if not response.body:
            return response

        for fmt, func in six.iteritems(self._formats):
            new_response = func(response)
            if new_response:
                return new_response
        return response
