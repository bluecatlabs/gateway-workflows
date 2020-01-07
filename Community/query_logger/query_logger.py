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

import os
import sys
import datetime
import re
import pytz
import json
import hashlib
import functools
from threading import Lock
from apscheduler.schedulers.background import BackgroundScheduler

from dnsedge.edgeapi import EdgeAPI


from .poller import Poller
from .edge_logging import EdgeLogger


class QueryLoggerException(Exception): pass


class QueryLogger(object):
    _unique_instance = None
    _lock = Lock()
    _config_file = os.path.dirname(os.path.abspath(__file__)) + '/config.json'

    @classmethod
    def __internal_new__(cls):
        return super().__new__(cls)

    @classmethod
    def get_instance(cls, debug=False):
        if cls._unique_instance is None:
            with cls._lock:
                if cls._unique_instance is None:
                    cls._unique_instance = cls.__internal_new__()
                    cls._unique_instance._debug = debug
                    cls._unique_instance._scheduler = None
                    cls._unique_instance._job = None
                    cls._unique_instance._edge_api = None
                    cls._unique_instance._poller = None
                    cls._unique_instance._load()
        return cls._unique_instance

    def _load(self):
        with open(QueryLogger._config_file) as f:
            self._config = json.load(f)

    def get_value(self, section, key):
        value = None
        with QueryLogger._lock:
            config = self._config[section]
            if key in config.keys():
                value = config[key]
        return value

    def set_value(self, section, key, value):
        with QueryLogger._lock:
            config = self._config[section]
            config[key] = value

    def save(self):
        with QueryLogger._lock:
            with open(QueryLogger._config_file, 'w') as f:
                json.dump(self._config, f, indent=4)


    def process_logs(self):
        if not self._edge_api.validate_edgeurl():
            return False

        succeed = False
        with QueryLogger._lock:
            self._poller.get_event_from_api(self._edge_api)
            succeed = True
        return succeed

    def _create_poller(self):
        app_logger = EdgeLogger('applog', self)
        data_logger = EdgeLogger('datalog', self)
        return Poller(self, app_logger, data_logger)

    def register_job(self):
        succeed = False
        try:
            interval = self.get_value('poll', 'interval')
            edge_api = EdgeAPI(self.get_value('edge', 'url'), debug=True)
            edge_api.set_token(self.get_value('edge', 'token'))
            poller = self._create_poller()
            if self._scheduler is None:
                self._scheduler = BackgroundScheduler(daemon=True, timezone=pytz.utc)
                self._scheduler.start()

            if self._job is not None:
                self._job.remove()
                self._job = None

            if self._edge_api is not None:
                self._edge_api = None

            if self._poller is not None:
                self._poller = None

            if interval is not None and 0 < interval:
                self._edge_api = edge_api
                self._poller = poller
                self._job = self._scheduler.add_job(self.process_logs, 'interval', seconds=interval)
                succeed = True

        except Exception as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return succeed
#
# Followings are code that should be executed when this module is loaded.
#

query_logger = QueryLogger.get_instance(debug=True)
print("QueryLogger is loaded.......")
if query_logger.register_job():
    print("Synchronization Job is registered.......")
