# Copyright (C) 2016  Custodia Project Contributors - see LICENSE file
"""FreeIPA vault store (PoC)
"""
import configparser

from custodia.plugin import CSStore, PluginOption, REQUIRED

from ipalib import api
from ipalib.errors import DuplicateEntry
from ipalib.constants import FQDN


class FreeIPA(object):
    """FreeIPA wrapper

    Custodia uses a forking server model. We can bootstrap FreeIPA API in
    the main process. Connections must be created in the client process.
    """
    def __init__(self, keytab=None, ccache=None, api=api, context='cli'):
        self._keytab = keytab
        self._ccache = ccache
        self._api = api
        self._context = context
        self._bootstrap()

    @property
    def Command(self):
        return self._api.Command

    def _bootstrap(self):
        if not self._api.isdone('bootstrap'):
            # set client keytab env var for authentication
            if self._keytab is not None:
                os.environ['KRB5_CLIENT_KTNAME'] = self._keytab
            if self._ccache is not None:
                os.environ['KRB5CCNAME'] = self._ccache

            self._api.bootstrap(context=self._context)
            self._api.finalize()

    def __enter__(self):
        if not self._api.Backend.rpcclient.isconnected():
            self._api.Backend.rpcclient.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._api.Backend.rpcclient.isconnected():
            self._api.Backend.rpcclient.disconnect()


class IpaVault(CSStore):
    principal = PluginOption('text', 'host/' + FQDN, None)

    def __init__(self, config, section=None):
        super(IpaVault, self).__init__(config, section)
        self.ipa = FreeIPA()
        with self.ipa:
            self.logger.info(repr(self.ipa.Command.ping()))

    def _mangle_key(self, key):
        if '__' in key:
            raise ValueError
        key = key.replace('/', '__')
        if isinstance(key, bytes):
            key = key.decode('utf-8')
        return key

    def get(self, key):
        key = self._mangle_key(key)
        with self.ipa as ipa:
            result = ipa.Command.vault_retrieve(key,
                                                service=self.principal)
        return result[u'result'][u'data']

    def set(self, key, value, replace=False):
        key = self._mangle_key(key)
        if not isinstance(value, bytes):
            value = value.encode('utf-8')
        with self.ipa as ipa:
            try:
                ipa.Command.vault_add(key,
                                      service=self.principal,
                                      ipavaulttype=u"standard")
            except DuplicateEntry:
                if not replace:
                    raise

            ipa.Command.vault_archive(key,
                                      data=value,
                                      service=self.principal)

    def span(self, key):
        raise NotImplementedError

    def list(self, keyfilter=None):
        with self.ipa as ipa:
            result = ipa.Command.vault_find(service=self.principal,
                                            ipavaulttype=u"standard")
        names = []
        for entry in result[u'result']:
            cn = entry[u'cn'][0]
            names.append(cn)
        return names

    def cut(self, key):
        key = self._mangle_key(key)
        with self.ipa as ipa:
            ipa.Command.vault_del(key, service=self.principal)


if __name__ == '__main__':
    parser = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation()
    )
    parser.read_string(u"""
    [vault]
    principal = host/clien1.ipa.example
    """)

    v = IpaVault(parser, "vault")
    v.set('foo', 'bar', replace=True)
    print(v.get('foo'))
    print(v.list())
    v.cut('foo')
    print(v.list())

