# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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
# limitations under the License

import os
import sys
import datetime
import pytz
import json
import hashlib
from threading import Lock
from apscheduler.schedulers.background import BackgroundScheduler

from dnsedge.edgeapi import EdgeAPI

class SPWatcherException(Exception): pass


class SPWatcher(object):
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
                    cls._unique_instance._service_points = []
                    cls._unique_instance._load()
        return cls._unique_instance

    def _load(self):
        with open(SPWatcher._config_file) as f:
            self._config = json.load(f)

    def get_value(self, key):
        value = None
        with SPWatcher._lock:
            if key in self._config.keys():
                value = self._config[key]
        return value

    def set_value(self, key, value):
        with SPWatcher._lock:
            self._config[key] = value

    def get_service_points(self):
        service_points = []
        with SPWatcher._lock:
            service_points = self._service_points
        return service_points

    def set_service_points(self, service_points):
        with SPWatcher._lock:
            self._service_points = service_points

    def clear_service_points(self):
        with SPWatcher._lock:
            self._service_points = []

    def save(self):
        with SPWatcher._lock:
            with open(SPWatcher._config_file, 'w') as f:
                json.dump(self._config, f, indent=4)

    def _construct_site_dic(self, edge_api):
        site_dic = {}
        sites = edge_api.get_sites()
        for site in sites:
            site_dic[site['id']] = site['name']
        return site_dic

    def _get_sp_status(self, edge_api, ipaddress):
        status = 'UNKNOWN'
        sp_status = edge_api.get_service_point_status(ipaddress)
        if sp_status is not None:
            status = sp_status['spStatus']
        else:
            status = 'UNREACHED'
        print('ipaddress<%s> status = <%s>' % (ipaddress, status))
        return status

    def _construct_linked_name(self, edge_api, name, ipaddress):
        return "<a href='%s'  target='_blank'>%s</a>" % \
            (edge_api.get_service_point_status_url(ipaddress), name)

    def _collect_service_points(self, edge_api):
        service_points = []
        site_dic = self._construct_site_dic(edge_api)
        sps = edge_api.get_service_points()
        for sp in sps:
            service_point = {}
            service_point['id'] = sp['id']
            service_point['name'] = sp['name']
            service_point['ipaddress'] = sp['ipAddresses'][0].split('/')[0] if 0 < len(sp['ipAddresses']) else ''
            service_point['site'] = site_dic[sp['siteId']] if sp['siteId'] in site_dic.keys() else ''
            service_point['connected'] = sp['connectionState']
            service_point['status'] = 'UNKNOWN'
            if service_point['ipaddress'] != '':
                service_point['name'] = \
                    self._construct_linked_name(edge_api, service_point['name'], service_point['ipaddress'])
                service_points.append(service_point)

        if 0 < len(service_points):
            service_points.sort(key=lambda x:x['site'])
        return service_points

    def watch_service_points(self):
        if self._debug:
            print('Watch Service Points is called....')
        edge_api = EdgeAPI(self.get_value('edge_url'), debug=self._debug)

        if not edge_api.validate_edgeurl():
            return False

        service_points = self.get_service_points()
        if 0 == len(service_points):
            if edge_api.login(self.get_value('edge_username'), self.get_value('edge_password')):
                service_points = self._collect_service_points(edge_api)
                self.set_service_points(service_points)
                edge_api.logout()

        for sp in service_points:
            sp['status'] = self._get_sp_status(edge_api, sp['ipaddress'])
        return True

    def register_job(self):
        succeed = False
        try:
            interval = self.get_value('execution_interval')
            edge_api = EdgeAPI(self.get_value('edge_url'), debug=True)
            if not edge_api.validate_edgeurl():
                return succeed

            if self._scheduler is None:
                self._scheduler = BackgroundScheduler(daemon=True, timezone=pytz.utc)
                self._scheduler.start()

            if self._job is not None:
                self._job.remove()
                self._job = None

            self.clear_service_points()
            if interval is not None and 0 < interval:
                self.watch_service_points()
                self._job = \
                    self._scheduler.add_job(self.watch_service_points, 'interval', seconds=interval)
                succeed = True

        except Exception as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return succeed
#
# Followings are code that should be executed when this module is loaded.
#

sp_watcher = SPWatcher.get_instance(debug=True)
print("SPWatcher is loaded.......")
if sp_watcher.register_job():
    print("Watching Job is registered.......")
