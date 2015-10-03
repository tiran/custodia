# Copyright (C) 2015  Custodia Project Contributors - see LICENSE file

import json
import uuid

from custodia import log
from custodia.client import CustodiaHTTPClient
from custodia.httpd.consumer import HTTPConsumer
from custodia.httpd.server import HTTPError


class Forwarder(HTTPConsumer):

    def __init__(self, *args, **kwargs):
        super(Forwarder, self).__init__(*args, **kwargs)
        self._auditlog = log.AuditLog(self.config)
        self.client = CustodiaHTTPClient(self.config['forward_uri'])
        self.headers = json.loads(self.config.get('forward_headers', '{}'))
        self.uuid = str(uuid.uuid4())
        self.headers['X-LOOP-CUSTODIA'] = self.uuid

    def _path(self, request):
        trail = request.get('trail', [])
        prefix = request.get('remote_user', 'guest')
        return '/'.join([prefix.rstrip('/')] + trail)

    def _headers(self, request):
        headers = {}
        headers.update(self.headers)
        loop = request['headers'].get('X-LOOP-CUSTODIA', None)
        if loop is not None:
            headers['X-LOOP-CUSTODIA'] += ',' + loop
        return self.headers

    def _response(self, reply, response):
        if reply.status_code < 200 or reply.status_code > 299:
            raise HTTPError(reply.status_code)
        response['code'] = reply.status_code
        if reply.content:
            response['output'] = reply.content

    def _request(fn):  # NOQA
        def request(self, request, response):
            if self.uuid in request['headers'].get('X-LOOP-CUSTODIA', ''):
                raise HTTPError(502, "Loop detected")
            r = fn(self, request, response)
            self._response(r, response)
        return request

    @_request
    def GET(self, request, response):
        return self.client.get(self._path(request),
                               params=request.get('query', None),
                               headers=self._headers(request))

    @_request
    def PUT(self, request, response):
        return self.client.put(self._path(request),
                               data=request.get('body', None),
                               params=request.get('query', None),
                               headers=self._headers(request))

    @_request
    def DELETE(self, request, response):
        return self.client.delete(self._path(request),
                                  params=request.get('query', None),
                                  headers=self._headers(request))

    @_request
    def POST(self, request, response):
        return self.client.post(self._path(request),
                                data=request.get('body', None),
                                params=request.get('query', None),
                                headers=self._headers(request))
