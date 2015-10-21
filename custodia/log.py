# Copyright (C) 2015  Custodia Project Contributors - see LICENSE file

import json
import logging
import logging.config
import os
import time

import six

custodia_logger = logging.getLogger('custodia')
custodia_logger.addHandler(logging.NullHandler())

HERE = os.path.dirname(os.path.abspath(__file__))
LOGGING_CONFIG = os.path.join(HERE, 'custodia.logging.json')


class UTCFormatter(logging.Formatter):
    converter = time.gmtime


def setup_logging(logcfg=LOGGING_CONFIG, debug=False,
                  auditlog='custodia.audit.log'):
    substitution = {
        "$AUDIT_LOG": auditlog,
        "$ROOT_LEVEL": 'DEBUG' if debug else 'INFO'
    }

    def object_hook(dct):
        for k, v in dct.items():
            if isinstance(v, six.text_type):
                dct[k] = substitution.get(v, v)
        return dct

    with open(logcfg) as f:
        cfg = json.load(f, object_hook=object_hook)

    logging.config.dictConfig(cfg)
    custodia_logger.info('Logging configuration %s loaded.', logcfg)


AUDIT_NONE = 0
AUDIT_GET_ALLOWED = 1
AUDIT_GET_DENIED = 2
AUDIT_SET_ALLOWED = 3
AUDIT_SET_DENIED = 4
AUDIT_DEL_ALLOWED = 5
AUDIT_DEL_DENIED = 6
AUDIT_LAST = 7
AUDIT_SVC_NONE = 8
AUDIT_SVC_AUTH_PASS = 9
AUDIT_SVC_AUTH_FAIL = 10
AUDIT_SVC_AUTHZ_PASS = 11
AUDIT_SVC_AUTHZ_FAIL = 12
AUDIT_SVC_LAST = 13
AUDIT_MESSAGES = [
    "AUDIT FAILURE",
    "ALLOWED: '%(client)s' requested key '%(key)s'",  # AUDIT_GET_ALLOWED
    "DENIED: '%(client)s' requested key '%(key)s'",   # AUDIT_GET_DENIED
    "ALLOWED: '%(client)s' stored key '%(key)s'",     # AUDIT_SET_ALLOWED
    "DENIED: '%(client)s' stored key '%(key)s'",      # AUDIT_SET_DENIED
    "ALLOWED: '%(client)s' deleted key '%(key)s'",    # AUDIT_DEL_ALLOWED
    "DENIED: '%(client)s' deleted key '%(key)s'",     # AUDIT_DEL_DENIED
    "AUDIT FAILURE 7",
    "AUDIT FAILURE 8",
    "PASS(%(tag)s): '%(cli)s' authenticated as '%(name)s'",  # SVC_AUTH_PASS
    "FAIL(%(tag)s): '%(cli)s' authenticated as '%(name)s'",  # SVC_AUTH_FAIL
    "PASS(%(tag)s): '%(cli)s' authorized for '%(name)s'",    # SVC_AUTHZ_PASS
    "FAIL(%(tag)s): '%(cli)s' authorized for '%(name)s'",    # SVC_AUTHZ_FAIL
    "AUDIT FAILURE 13",
]


class AuditLog(object):
    def __init__(self, logger):
        self.logger = logger

    def key_access(self, action, client, keyname):
        if action <= AUDIT_NONE or action >= AUDIT_LAST:
            action = AUDIT_NONE
        msg = AUDIT_MESSAGES[action]
        args = {'client': client, 'key': keyname}
        self.logger.info(msg, args)

    def svc_access(self, action, client, tag, name):
        if action <= AUDIT_SVC_NONE or action >= AUDIT_SVC_LAST:
            action = AUDIT_NONE
        msg = AUDIT_MESSAGES[action]
        args = {'cli': client, 'tag': tag, 'name': name}
        self.logger.info(msg, args)

auditlog = AuditLog(logging.getLogger('custodia.audit'))
