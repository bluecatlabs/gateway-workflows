# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates
# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -Original creation info-
# By: Akira Goto (agoto@bluecatnetworks.com)
# Date: 2019-08-28
# Gateway Version: 19.5.1
#
# -Update info-
# By: Akira Goto (agoto@bluecatnetworks.com)
# Date: 2021-01-07
# Gateway Version: 20.12.1
# Description: Service Point Watcher sp_watcher.py

import os
import sys
import pytz
import json
from datetime import datetime, timedelta
from pytz import timezone
from threading import Lock
from apscheduler.schedulers.background import BackgroundScheduler

from dnsedge.edgeapi import EdgeAPI
from .snmp_trap_sender import send_status_notification, send_pulling_stopped_notification
from .state_logger import StateLogger

class SPWatcherException(Exception): pass


class SPWatcher(object):
    _unique_instance = None
    _lock = Lock()
    _service_points_file = os.path.dirname(os.path.abspath(__file__)) + '/service_points.json'
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
                    cls._unique_instance._state_logger = StateLogger()
        return cls._unique_instance

    def _load(self):
        with open(SPWatcher._service_points_file) as f:
            self._service_points = json.load(f)
        # For compatibility
        for sp in self._service_points:
            if 'watch' not in sp.keys():
                sp['watch'] = 'True'

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

    def get_service_point_summaries(self):
        service_points = self.get_service_points()
        service_point_summaries = []
        for sp in service_points:
            sps = {}
            sps['id'] = sp['id']
            sps['watch'] = sp['watch']
            sps['name'] = sp['linked_name']
            sps['ipaddress'] = sp['ipaddress']
            sps['site'] = sp['site']
            sps['connected'] = sp['connected']
            sps['status'] = sp['status']
            sps['pulling_severity'] = sp['pulling_severity']
            service_point_summaries.append(sps)
        return service_point_summaries

    def set_service_points(self, service_points):
        with SPWatcher._lock:
            self._service_points = service_points

    def clear_service_points(self):
        with SPWatcher._lock:
            self._service_points = []

    def save(self):
        with SPWatcher._lock:
            with open(SPWatcher._service_points_file, 'w') as f:
                json.dump(self._service_points, f, indent=4)
            with open(SPWatcher._config_file, 'w') as f:
                json.dump(self._config, f, indent=4)

    def _construct_site_dic(self, edge_api):
        site_dic = {}
        sites = edge_api.get_sites()
        for site in sites:
            site_dic[site['id']] = site['name']
        return site_dic

    def _issue_traps(self, service_point, status, sp_status):
        trap_servers = self._config['trap_servers']
        pulling_severity = 'UNKNOWN'
        if service_point['status'] != 'UNKNOWN' and service_point['status'] != status:
            send_status_notification(
                trap_servers,
                service_point,
                'spStatus',
                status
            )
            self._state_logger.log_status_notification(
                service_point,
                'spStatus',
                status
            )

        if service_point['diagnostics'] is not None:
            prev_sp_statuses = service_point['diagnostics']['spServicesStatuses']
            crnt_sp_statuses = sp_status['spServicesStatuses']
            for key in crnt_sp_statuses.keys():
                if prev_sp_statuses[key]['status'] != crnt_sp_statuses[key]['status']:
                    send_status_notification(
                        trap_servers,
                        service_point,
                        key,
                        crnt_sp_statuses[key]['status']
                    )
                    self._state_logger.log_status_notification(
                        service_point,
                        key,
                        crnt_sp_statuses[key]['status']
                    )

            if 'dns-gateway-service' in crnt_sp_statuses.keys():
                getway_service = crnt_sp_statuses['dns-gateway-service']
                if 'additionalDetails' in getway_service.keys():
                    additional_details = getway_service['additionalDetails']
                    last_pulling_timestamp = \
                        additional_details['settingsDiagnostics']['lastSettingsPollingTimestamp'] // 1000
                    last_pulling_time = datetime.fromtimestamp(last_pulling_timestamp)
                    now = datetime.now()

                    delay = now - last_pulling_time
                    if delay > timedelta(hours=1):
                        pulling_severity = 'CRITICAL'
                    elif delay > timedelta(minutes=15):
                        pulling_severity = 'WARNING'
                    else:
                        pulling_severity = 'NORMAL'
                    if service_point['pulling_severity'] != 'UNKNOWN' and \
                       service_point['pulling_severity'] != pulling_severity:
                        send_pulling_stopped_notification(
                            trap_servers,
                            service_point,
                            pulling_severity,
                            last_pulling_time
                        )
                        self._state_logger.log_pulling_stopped_notification(
                            service_point,
                            pulling_severity,
                            last_pulling_time
                        )

        return pulling_severity

    def _analyze_service_point(self, edge_api, service_point, timeout):
        status = 'UNKNOWN'
        sp_status = edge_api.get_service_point_status(service_point['ipaddress'], timeout)
        pulling_severity = 'UNKNOWN'
        if sp_status is not None:
            status = sp_status['spStatus']
            pulling_severity = self._issue_traps(service_point, status, sp_status)
        else:
            status = 'UNREACHED'
            if service_point['status'] != 'UNKNOWN' and service_point['status'] != status:
                send_status_notification(
                    self._config['trap_servers'],
                    service_point,
                    'spStatus',
                    status
                )
                self._state_logger.log_status_notification(
                    service_point,
                    'spStatus',
                    status
                )

        service_point['status'] = status
        service_point['diagnostics'] = sp_status
        service_point['pulling_severity'] = pulling_severity

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
            service_point['watch'] = 'True'
            service_point['name'] = sp['name']
            service_point['ipaddress'] = sp['ipAddresses'][0].split('/')[0] if 0 < len(sp['ipAddresses']) else ''
            service_point['site'] = site_dic[sp['siteId']] if sp['siteId'] in site_dic.keys() else ''
            service_point['connected'] = sp['connectionState']
            service_point['status'] = 'UNKNOWN'
            service_point['diagnostics'] = None
            service_point['pulling_severity'] = 'UNKNOWN'
            service_point['linked_name'] = service_point['name']
            if service_point['ipaddress'] != '':
                service_point['linked_name'] = \
                    self._construct_linked_name(edge_api, service_point['name'], service_point['ipaddress'])
                service_points.append(service_point)

        if 0 < len(service_points):
            service_points.sort(key=lambda x:x['site'])
        return service_points

    def _find_service_points(self, id):
        found = None
        for sp in self.get_service_points():
            if sp['id'] == id:
                found = sp
                break
        return found

    def watch_service_points(self):
        edge_api = EdgeAPI(self.get_value('edge_url'), debug=False)
        service_points = self.get_service_points()
        if 0 == len(service_points):
            return False

        timeout = self.get_value('timeout')
        for sp in service_points:
            if sp['watch'] == 'True':
                self._analyze_service_point(edge_api, sp, timeout)
        return True

    def collect_service_points(self):
        succeed = False
        try:
            interval = self.get_value('execution_interval')
            edge_api = EdgeAPI(self.get_value('edge_url'), debug=True)
            if not edge_api.validate_edgeurl():
                return succeed
            if edge_api.login(self.get_value('edge_client_id'), self.get_value('edge_secret')):
                service_points = self._collect_service_points(edge_api)
                self.set_service_points(service_points)
                edge_api.logout()

        except Exception as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return succeed

    def update_service_points(self, service_points):
        succeed = False
        updated_sps = []
        for sp in service_points:
            found = self._find_service_points(sp['id'])
            if found is not None:
                found['watch'] = sp['watch']
                updated_sps.append(found)
        self.set_service_points(updated_sps)
        return succeed

    def register_job(self):
        succeed = False
        try:
            edge_api = EdgeAPI(self.get_value('edge_url'), debug=False)
            if not edge_api.validate_edgeurl():
                return succeed

            if self._scheduler is None:
                self._scheduler = BackgroundScheduler(daemon=True, timezone=pytz.utc)
                self._scheduler.start()

            if self._job is not None:
                self._job.remove()
                self._job = None

            interval = self.get_value('execution_interval')
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
