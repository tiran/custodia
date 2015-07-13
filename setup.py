#!/usr/bin/python
#
# Copyright (C) 2015  Custodia project Contributors, for licensee see COPYING

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requirements = []
with open('requirements.txt') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            requirements.append(line.strip())

with open('README') as f:
    long_description=f.read()

setup(
    name = 'custodia',
    version = '0.0.1',
    license = 'GPLv3+',
    description='A service to manage, retrieve and store secrets',
    long_description=long_description,
    maintainer = 'Custodia project Contributors',
    maintainer_email = 'simo@redhat.com',
    url='https://github.com/simo5/custodia',
    packages = ['custodia', 'custodia.httpd', 'custodia.store'],
    data_files = [('share/man/man7', ['man/custodia.7']),
                  ('share/doc/custodia', ['LICENSE', 'README']),
                  ('share/doc/custodia/examples', ['custodia.conf']),
                 ],
    scripts = ['custodia/custodia'],
    install_requires=requirements,
    tests_require=['tox'] + requirements,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Security :: Cryptography',
    ],

)

