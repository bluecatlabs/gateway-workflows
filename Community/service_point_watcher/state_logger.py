# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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
# By: Akira Goto (agoto@bluecatnetworks.com)
# Date: 2019-08-28
# Gateway Version: 19.5.1
# Description: Service Point Watcher state_logger.py

import logging
import os
import sys

class StateLogger(object):
    _base_directory = 'logs'
    _logger = None
    
    def __init__(self, level = 20):
        self._logger = logging.getLogger('Status Logger')
        self._logger.setLevel(level)
        fh = logging.FileHandler(os.path.join(self._base_directory, 'sp_status.log'))
        formatter = logging.Formatter('Service Point Watcher:%(asctime)s UTC:%(levelname)s:%(message)s')
        self._logger.addHandler(fh)
        fh.setFormatter(formatter)
        
        
    def log_status_notification(self, service_point, service, status):
        msg = '<%s> <%s> status has been changed to <%s>.' % (service_point['name'], service, status)
        if status == 'GOOD':
            self._logger.info(msg)
        else:
            if service == 'naming-service' or status == 'UNREACHED':
                self._logger.critical(msg)
            else:
                self._logger.error(msg)
                
    def log_pulling_stopped_notification(self, service_point, pulling_severity, last_pulling_time):
        msg = '<%s> pulling severity has been changed to <%s>.' % (service_point['name'], pulling_severity)
        if pulling_severity == 'NORMAL':
            self._logger.info(msg)
        elif pulling_severity == 'WARNING':
            self._logger.warning(msg)
        elif pulling_severity == 'CRITICAL':
            self._logger.error(msg)

