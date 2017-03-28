#!/usr/bin/python
#
# Copyright (C) 2015  Custodia project Contributors, for licensee see COPYING

import sys

import setuptools
from setuptools import setup

SETUPTOOLS_VERSION = tuple(int(v) for v in setuptools.__version__.split("."))


requirements = [
    'cryptography',
    'jwcrypto',
    'six',
    'requests'
]

# extra requirements
etcd_requires = ['python-etcd']
ipa_requires = ['ipalib >= 4.5.0', 'ipaclient >= 4.5.0']

# test requirements
test_requires = ['coverage', 'pytest', 'mock'] + etcd_requires + ipa_requires

extras_require = {
    'etcd_store': etcd_requires,
    'ipa': ipa_requires,
    'test': test_requires,
    'test_docs': ['docutils', 'markdown'] + etcd_requires,
    'test_pep8': ['flake8', 'flake8-import-order', 'pep8-naming'],
    'test_pylint': ['pylint'] + test_requires,
}

# backwards compatibility with old setuptools
# extended interpolation is provided by stdlib in Python 3.4+
# if SETUPTOOLS_VERSION < (18, 0, 0) and sys.version_info < (3, 4):
#     requirements.append('configparser')
# else:
#     extras_require[':python_version<"3.4"'] = ['configparser']


with open('README') as f:
    long_description = f.read()


# Plugins
custodia_authenticators = [
    'SimpleCredsAuth = custodia.httpd.authenticators:SimpleCredsAuth',
    'SimpleHeaderAuth = custodia.httpd.authenticators:SimpleHeaderAuth',
    'SimpleAuthKeys = custodia.httpd.authenticators:SimpleAuthKeys',
    ('SimpleClientCertAuth = '
     'custodia.httpd.authenticators:SimpleClientCertAuth'),
]

custodia_authorizers = [
    'SimplePathAuthz = custodia.httpd.authorizers:SimplePathAuthz',
    'UserNameSpace = custodia.httpd.authorizers:UserNameSpace',
    'KEMKeysStore = custodia.message.kem:KEMKeysStore',
]

custodia_clients = [
    'KEMClient = custodia.client:CustodiaKEMClient',
    'SimpleClient = custodia.client:CustodiaSimpleClient',
]

custodia_consumers = [
    'Forwarder = custodia.forwarder:Forwarder',
    'Secrets = custodia.secrets:Secrets',
    'Root = custodia.root:Root',
]

custodia_stores = [
    'EncryptedOverlay = custodia.store.encgen:EncryptedOverlay',
    'EncryptedStore = custodia.store.enclite:EncryptedStore',
    'IPAVault = custodia.ipa.vault:IPAVault',
    'EtcdStore = custodia.store.etcdstore:EtcdStore',
    'SqliteStore = custodia.store.sqlite:SqliteStore',
]


setup(
    name='custodia',
    description='A service to manage, retrieve and store secrets',
    long_description=long_description,
    version='0.3.0',
    license='GPLv3+',
    maintainer='Custodia project Contributors',
    maintainer_email='simo@redhat.com',
    url='https://github.com/latchset/custodia',
    namespace_packages=['custodia'],
    packages=[
        'custodia',
        'custodia.cli',
        'custodia.httpd',
        'custodia.ipa',
        'custodia.message',
        'custodia.server',
        'custodia.store',
        'custodia.vendor',
        'custodia.vendor.backports',
        'custodia.vendor.backports.configparser',
    ],
    entry_points={
        'console_scripts': [
            'custodia = custodia.server:main',
            'custodia-cli = custodia.cli:main',
        ],
        'custodia.authenticators': custodia_authenticators,
        'custodia.authorizers': custodia_authorizers,
        'custodia.clients': custodia_clients,
        'custodia.consumers': custodia_consumers,
        'custodia.stores': custodia_stores,
    },
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=requirements,
    tests_require=test_requires,
    extras_require=extras_require,
)
