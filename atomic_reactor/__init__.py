"""
Copyright (c) 2015 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the BSD license. See the LICENSE file for details.


constants
"""

from locale import nl_langinfo, CODESET
import logging
from os import fdopen, dup
import sys
import time

from atomic_reactor.version import __version__

try:
    from osbs.constants import ATOMIC_REACTOR_LOGGING_FMT
except ImportError:
    # not available in osbs < 0.41
    fmt = '%(asctime)s platform:%(arch)s - %(name)s - %(levelname)s - %(message)s'
    ATOMIC_REACTOR_LOGGING_FMT = fmt

start_time = time.time()


class ArchFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'arch'):
            record.arch = '-'

        return super(ArchFormatter, self).format(record)


class EncodedStream(object):
    def __init__(self, fileno, encoding):
        self.binarystream = fdopen(dup(fileno), 'wb')
        self.encoding = encoding

    def write(self, text):
        self.binarystream.write(text.encode(self.encoding))


def set_logging(name="atomic_reactor", level=logging.DEBUG, handler=None):
    # create logger
    logger = logging.getLogger(name)
    logger.handlers = []
    logger.setLevel(level)

    if not handler:
        # create console handler and set level to debug
        log_encoding = nl_langinfo(CODESET)
        encoded_stream = EncodedStream(sys.stderr.fileno(), log_encoding)
        handler = logging.StreamHandler(encoded_stream)
        handler.setLevel(logging.DEBUG)

        # create formatter
        formatter = ArchFormatter(ATOMIC_REACTOR_LOGGING_FMT)

        # add formatter to ch
        handler.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(handler)


set_logging(level=logging.WARNING)  # override this however you want
