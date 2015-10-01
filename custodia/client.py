# Copyright (C) 2015  Custodia Project Contributors - see LICENSE file

import json
import socket

import requests

from requests.adapters import HTTPAdapter
from requests.compat import unquote, urlparse

from requests.packages.urllib3.connection import HTTPConnection
from requests.packages.urllib3.connectionpool import HTTPConnectionPool


class HTTPUnixConnection(HTTPConnection):

    def __init__(self, host, timeout=60, **kwargs):
        super(HTTPConnection, self).__init__('localhost')
        self.unix_socket = host
        self.timeout = timeout

    def connect(self):
        s = socket.socket(family=socket.AF_UNIX)
        s.settimeout(self.timeout)
        s.connect(self.unix_socket)
        self.sock = s


class HTTPUnixConnectionPool(HTTPConnectionPool):

    scheme = 'http+unix'
    ConnectionCls = HTTPUnixConnection


class HTTPUnixAdapter(HTTPAdapter):

    def get_connection(self, url, proxies=None):
        # proxies, silently ignored
        path = unquote(urlparse(url).netloc)
        return HTTPUnixConnectionPool(path)


DEFAULT_HEADERS = {'Content-Type': 'application/json'}


class CustodiaHTTPClient(object):

    def __init__(self, url):
        self.session = requests.Session()
        self.session.mount('http+unix://', HTTPUnixAdapter())
        self.headers = DEFAULT_HEADERS
        self.url = url

    def set_simple_auth_keys(self, name, key,
                             name_header='CUSTODIA_AUTH_ID',
                             key_header='CUSTODIA_AUTH_KEY'):
        self.headers[name_header] = name
        self.headers[key_header] = key

    def _join_url(self, path):
        return self.url.rstrip('/') + '/' + path.lstrip('/')

    def _add_headers(self, **kwargs):
        headers = kwargs.get('headers', None)
        if headers is None:
            headers = dict()
        headers.update(self.headers)
        return headers

    def _decorator(fn):  # NOQA
        def decoration(self, path, **kwargs):
            url = self._join_url(path)
            kwargs['headers'] = self._add_headers(**kwargs)
            return fn(self, url, **kwargs)
        return decoration

    @_decorator
    def delete(self, path, **kwargs):
        return self.session.delete(path, **kwargs)

    @_decorator
    def get(self, path, **kwargs):
        return self.session.get(path, **kwargs)

    @_decorator
    def head(self, path, **kwargs):
        return self.session.head(path, **kwargs)

    @_decorator
    def patch(self, path, **kwargs):
        return self.session.patch(path, **kwargs)

    @_decorator
    def post(self, path, **kwargs):
        return self.session.post(path, **kwargs)

    @_decorator
    def put(self, path, **kwargs):
        return self.session.put(path, **kwargs)


class CustodiaClient(CustodiaHTTPClient):

    def create_container(self, name):
        r = self.post(name if name.endswith('/') else name + '/')
        r.raise_for_status()

    def delete_container(self, name):
        r = self.delete(name if name.endswith('/') else name + '/')
        r.raise_for_status()

    def list_container(self, name, filter=None):
        params = None
        if filter is not None:
            params = 'filter=%s' % filter
        r = self.get(name if name.endswith('/') else name + '/',
                     params=params)
        r.raise_for_status()
        return r.text

    def get_key(self, name):
        r = self.get(name)
        r.raise_for_status()
        return r.text

    def set_key(self, name, data):
        r = self.put(name, data=data)
        r.raise_for_status()

    def del_key(self, name):
        r = self.delete(name)
        r.raise_for_status()

    def get_simple_key(self, name):
        data = self.get_key(name)
        simple = json.loads(data)
        ktype = simple.get("type", None)
        if ktype != "simple":
            raise TypeError("Invalid key type: %s" % ktype)
        return simple["value"]

    def set_simple_key(self, name, value):
        data = json.dumps({"type": "simple", "value": value})
        self.set_key(name, data)
