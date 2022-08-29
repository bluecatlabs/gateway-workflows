# Copyright 2022 BlueCat Networks (USA) Inc. and its affiliates
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
# By: BlueCat Networks Inc.
# Date: 2022-05-01
# Gateway Version: 21.11.2
# Description: Health Telemetries Endpoint telemetry_buffer.py

import json
import os
import sys
import traceback

from datetime import datetime, timezone, timedelta
from dateutil import parser

from collections import OrderedDict

import config.default_config as config

from .telemetry_store import TelemetryFileStore

CONFIG_FILE = '%s/config_%s.json'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

def get_system_local_tz():
    now = datetime.now()
    local_now = now.astimezone()
    return local_now.tzinfo

def _get_log_value(keys, log):
    value = None
    if log is not None:
        key_list = keys.split('.')
        key = key_list.pop(False)
        if 0 == len(key_list):
            value = log.get(key)
        else:
            log = log.get(key)
            keys = '.'.join(key_list)
            if type(log) is list:
                values = list(map(lambda d: _get_log_value(keys, d), log))
                value = ','.join(values)
            else:
                value = _get_log_value(keys, log)
    return value
    
def _is_match(filters, log):
    result = True
    for filter in filters:
        value = _get_log_value(filter['key'], log)
        if value != filter['value']:
            result = False
            break
    return result
    
def _convert_log(tz, fields, log):
    data = {}
    for field in fields:
        value = _get_log_value(field['data_id'], log)
        if field['type'] == 'datetime':
            datetime_value = datetime.fromtimestamp(value/1000000000)
            value = datetime_value.strftime(DATETIME_FORMAT)
        elif field['type'] == 'datetime_string':
            datetime_value = parser.parse(value).astimezone(tz)
            value = datetime_value.strftime(DATETIME_FORMAT)
        data[field['id']] = value
    return data
    
class TBException(Exception): pass

class TelemetryBuffer(object):
    _unique_instance = None
    _config_file = CONFIG_FILE % (os.path.dirname(os.path.abspath(__file__)), config.language)
    
    @classmethod
    def __internal_new__(cls):
        return super().__new__(cls)

    @classmethod
    def get_instance(cls, debug=False):
        if cls._unique_instance is None:
            cls._unique_instance = cls.__internal_new__()
            cls._unique_instance._local_tz = get_system_local_tz()
            cls._unique_instance._debug = debug
            cls._unique_instance._buffers = {
                'activity': OrderedDict(), 
                'dns': OrderedDict(),
                'dhcp': OrderedDict()
            }
            cls._unique_instance._strage = {
                'activity': TelemetryFileStore('activity'), 
                'dns': TelemetryFileStore('dns'),
                'dhcp': TelemetryFileStore('dhcp')
            }
            cls._unique_instance._load()
        return cls._unique_instance
        
    def _load(self):
        with open(TelemetryBuffer._config_file) as f:
            self._config = json.load(f)
            
    def get_buffers(self, buffer_type):
        return self._buffers[buffer_type]
        
    def get_field(self, buffer_type, id):
        fields = self._config[buffer_type]['fields']
        founds = [x for x in fields if x['id'] == id]
        return founds[0] if 0 < len(founds) else None
        
    def get_fields(self, buffer_type):
        return self._config[buffer_type]['fields']
        
    def get_data(self, buffer_type, key):
        data = {}
        buffer = self._buffers[buffer_type]
        if key in buffer.keys():
            data = buffer[key]
        return data
        
    def push(self, buffer_type, key, data):
        buffer = self._buffers[buffer_type]
        buffer[key] = data
        if self._config['max_buffer_size'] < len(buffer) :
            buffer.popitem(False)
            
        if self._config[buffer_type]['store']:
            self._strage[buffer_type].append(data)
            
    def collect_data(self, buffer_type, index=0, count=100):
        data = []
        filters = self._config[buffer_type]['filters']
        fields = self._config[buffer_type]['fields']
        pos = 0
        for log in reversed(self._buffers[buffer_type].values()):
            if _is_match(filters, log):
                if index <= pos:
                    data.append(_convert_log(self._local_tz, fields, log))
                    pos += 1
                    count -= 1
            if 0 >= count:
                break
        return data

#
# For temporally fix Warring Message at python 3.9
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

#
# Followings are code that should be executed when this module is loaded.
#
t_buffer = TelemetryBuffer.get_instance(debug=True)
print("TelemetryBuffer is loaded.......")
