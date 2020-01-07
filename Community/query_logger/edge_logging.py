# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Copyright BlueCat Networks, Inc. 2019
"""
__author__ = 'BlueCat Networks'

import logging
from logging.handlers import SysLogHandler
import socket


class EdgeLogger(object):
    """Configure logging based on configuration"""

    def __init__(self, name, cfg):
        log_type = cfg.get_value(name, 'type')
        logger = logging.getLogger(cfg.get_value(name, 'logger_name'))
        formatter = logging.Formatter(cfg.get_value(name, 'logger_formatter'),
                                      cfg.get_value(name, 'time_formatter'))
        if log_type == 'file':
            logger.setLevel(cfg.get_value(name, 'log_level'))
            handler = logging.handlers.TimedRotatingFileHandler(
                cfg.get_value(name, 'file_name'), when="H", interval=24, backupCount=10)
        elif log_type == 'leef':
            protocol = cfg.get_value(name, 'protocol')
            socket_type = socket.SOCK_STREAM if protocol == 'tcp' else socket.SOCK_DGRAM
            logger.setLevel(logging.INFO)
            handler = SysLogHandler(address=(
                cfg.get_value(name, 'server'), cfg.get_value(name, 'port')),
                        facility=logging.handlers.SysLogHandler.LOG_LOCAL1, socktype=socket_type)
        else:
            raise NameError('No valid log_type ' + log_type + ', valid values are file or leef')
        logger.addHandler(handler)
        handler.setFormatter(formatter)
        self._store = logger
        self._handler = handler

    def __del__(self):
        self._store.removeHandler(self._handler)

    def info(self, message):
        """Write INFO message to log."""
        self._store.info(message)

    def error(self, message):
        """Write ERROR message to log."""
        self._store.error(message)

    def fatal(self, message):
        """Write FATAL message to log."""
        self._store.fatal(message)

    def debug(self, message):
        """Write DEBUG message to log."""
        self._store.debug(message)
