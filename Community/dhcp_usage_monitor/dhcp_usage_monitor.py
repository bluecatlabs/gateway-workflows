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
# By: BlueCat Networks
# Date: 2022-07-10
# Gateway Version: 22.4.1
# Description: DHCP Usage Monitor 

import copy
import json
import os
import psycopg2
import pytz
import sys
import traceback

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from pysnmp.hlapi import *
from pytz import timezone
from threading import Lock

from bluecat import route, util
from bluecat_libraries.address_manager.api import Client
import config.default_config as config

from .dhcp_usage import calc_network_usage, get_network_id, get_network_suggestions
import warnings
warnings.simplefilter("ignore")

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))
    
mp_model = {
    'v1': 0,
    'v2c': 1
}
status_strings = {
    'UNKNOWN': 'Unknown',
    'NORMAL': 'Normal',
    'LOWER': 'Low',
    'HIGHER': 'High'
}

def send_dhcp_alart_notification(trap_servers, message):
    for trap_server in trap_servers:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            sendNotification(
                SnmpEngine(),
                CommunityData(trap_server['comstr'], mpModel=mp_model[trap_server['snmpver']]),
                UdpTransportTarget((trap_server['ipaddress'], trap_server['port'])),
                ContextData(),
                'trap',
                NotificationType(
                    ObjectIdentity('1.3.6.1.4.1.13315.100.210.255.1')
                ).addVarBinds(
                    ('1.3.6.1.4.1.13315.100.210.1.1.3', OctetString(message))
                )
            )
        )
        if errorIndication:
            print(errorIndication)


class DUMonitorException(Exception): pass


class DUMonitor(object):
    _unique_instance = None
    _lock = Lock()
    _dhcp_usages_file = os.path.dirname(os.path.abspath(__file__)) + '/dhcp_usages.json'
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
                    cls._unique_instance._dhcp_usages = []
                    cls._unique_instance._load()
        return cls._unique_instance
        
    def _load(self):
        with open(DUMonitor._dhcp_usages_file) as f:
            self._dhcp_usages = json.load(f)
            
        with open(DUMonitor._config_file) as f:
            self._config = json.load(f)
            
    def get_value(self, key):
        value = None
        with DUMonitor._lock:
            if key in self._config.keys():
                value = self._config[key]
        return value
        
    def set_value(self, key, value):
        with DUMonitor._lock:
            self._config[key] = value
            
    def get_dhcp_usages(self):
        dhcp_usages = []
        with DUMonitor._lock:
            dhcp_usages = self._dhcp_usages
        return dhcp_usages
        
    def add_dhcp_usage(self, dhcp_usage):
        dhcp_usages = []
        with DUMonitor._lock:
            self._dhcp_usages.append(dhcp_usage)
            
    def set_dhcp_usages(self, dhcp_usages):
        with DUMonitor._lock:
            self._dhcp_usages = dhcp_usages
            
    def get_trap_servers(self):
        trap_servers = []
        with DUMonitor._lock:
            trap_servers = self._config['trap_servers']
        return trap_servers
        
    def set_trap_servers(self, trap_servers):
        with DUMonitor._lock:
            self._config['trap_servers'] = trap_servers
            
    def clear_dhcp_usages(self):
        with DUMonitor._lock:
            self._dhcp_usages = []
            
    def save(self, only_dhcp_usages=False):
        with DUMonitor._lock:
            with open(DUMonitor._dhcp_usages_file, 'w') as f:
                json.dump(self._dhcp_usages, f, indent=4)
            if only_dhcp_usages == False:
                with open(DUMonitor._config_file, 'w') as f:
                    json.dump(self._config, f, indent=4)
                
    def get_network_id(self, api, config_id, cidr):
        return get_network_id(api, config_id, cidr)
        
    def calc_dhcp_usage(self, api, connector, network_id):
        return calc_network_usage(api, connector, network_id)
        
    def get_network_suggestions(self, api, config_id, cidr):
        return get_network_suggestions(api, config_id, cidr)
        
    def get_status(self, dhcp_usage):
        if dhcp_usage['id'] == 0:
            return 'UNKNOWN'
            
        status = 'NORMAL'
        if dhcp_usage['usage'] < dhcp_usage['low_watermark']:
            status = 'LOWER'
        elif dhcp_usage['high_watermark'] < dhcp_usage['usage']:
            status = 'HIGHER'
        return status
        
    def get_dhcp_usage(self, api, network_id, range, low_watermark, high_watermark):
        dhcp_usage = {
            'id': network_id,
            'range': range,
            'status': 'UNKNOWN',
            'low_watermark': low_watermark,
            'high_watermark': high_watermark,
            'usage': 0,
            'dhcp_count': 0,
            'leased_count': 0
        }
        
        dhcp_count = 0
        leased_count = 0
        usage = 0
        
        if network_id != 0:
            with psycopg2.connect(host=self.get_value('bam_ip'),
                database='proteusdb', user='bcreadonly') as connector:
                dhcp_count, leased_count, usage = self.calc_dhcp_usage(api, connector, network_id)
            dhcp_usage['dhcp_count'] = dhcp_count
            dhcp_usage['leased_count'] = leased_count
            dhcp_usage['usage'] = usage
            dhcp_usage['status'] = self.get_status(dhcp_usage)
        return dhcp_usage
        
    def issue_dhcp_alart(self, dhcp_usage):
        text=util.get_text(module_path(), config.language)
        message = text['dhcp_alert_message'].format(
            network=dhcp_usage['range'],
            status=status_strings[dhcp_usage['status']],
            usage=dhcp_usage['usage'],
            low_watermark=dhcp_usage['low_watermark'],
            high_watermark=dhcp_usage['high_watermark']
        )
        print(message)
        send_dhcp_alart_notification(self.get_trap_servers(), message)
        
    def monitor_dhcp_usages(self):
        dhcp_usages = self.get_dhcp_usages()
        updated_dus = []
        if 0 == len(dhcp_usages):
            return False
        bam_ip = self.get_value('bam_ip')
        with Client(f"http://{bam_ip}") as client:
            client.login(self.get_value('bam_user'), self.get_value('bam_pass'))
            try:
                with psycopg2.connect(host=self.get_value('bam_ip'),
                    database='proteusdb', user='bcreadonly') as connector:
                    
                    for du in dhcp_usages:
                        dhcp_usage = \
                            self.get_dhcp_usage(client, du['id'], du['range'],
                                du['low_watermark'], du['high_watermark'])
                        if du['status'] != dhcp_usage['status']:
                            self.issue_dhcp_alart(dhcp_usage)
                        updated_dus.append(dhcp_usage)
                        
                self.set_dhcp_usages(updated_dus)
                self.save(only_dhcp_usages=True)
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                
            client.logout()
            
        return True
        
    def register_job(self):
        succeed = False
        try:
            if self._scheduler is None:
                self._scheduler = BackgroundScheduler(daemon=True, timezone=pytz.utc)
                self._scheduler.start()
                
            if self._job is not None:
                self._job.remove()
                self._job = None
                
            interval = self.get_value('execution_interval')
            if interval is not None and 0 < interval:
                self.monitor_dhcp_usages()
                self._job = \
                    self._scheduler.add_job(self.monitor_dhcp_usages, 'interval', seconds=interval)
                succeed = True
                print("Job monitor_dhcp_usages is registerd interval(%d)" % interval)
                
        except Exception as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return succeed
#
# Followings are code that should be executed when this module is loaded.
#

du_monitor = DUMonitor.get_instance(debug=True)
print("DHCP Usage Monitor is loaded.......")
if du_monitor.register_job():
    print("Monitor Job is registered.......")
