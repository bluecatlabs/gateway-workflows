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
# Description: Health Telemetries Store telemetry_store.py

import json
import os
import sys
import traceback
import zipfile

from datetime import datetime, timezone, timedelta
from dateutil import parser

from collections import OrderedDict

import config.default_config as config

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
FILENAME_FORMAT = '/logs/%s_%s'
LOG_EXTENTION = '.log'
ZIP_EXTENTION = '.zip'
ROTATE_COUNT = 3000

class TelemetryFileStore(object):
    def __init__(self, type):
        datetime_string = datetime.now().strftime(DATETIME_FORMAT)
        self._type = type
        self._current_filename = FILENAME_FORMAT % (self._type, datetime_string)
        self._line_count = 0
        if os.path.exists(self._get_log_filename()):
            self._rotate_file(False)
            self._current_filename = self._current_filename + '_2'
            
    def _get_log_filename(self):
        return self._current_filename + LOG_EXTENTION
        
    def _get_zip_filename(self):
        return self._current_filename + ZIP_EXTENTION
        
    def _rotate_file(self, renew):
        with zipfile.ZipFile(self._get_zip_filename(), 'w',
            compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            log_filename = self._get_log_filename()
            zf.write(log_filename, arcname=os.path.basename(log_filename))
        os.remove(self._get_log_filename())
            
        if renew:
            datetime_string = datetime.now().strftime(DATETIME_FORMAT)
            self._current_filename = FILENAME_FORMAT % (self._type, datetime_string)
            self._line_count = 0
        
    def append(self, log):
        if ROTATE_COUNT <= self._line_count:
            self._rotate_file(True)
            
        with open(self._get_log_filename(), 'a') as f:
            line = json.dumps(log) + '\n'
            f.write(line)
            
        self._line_count += 1
