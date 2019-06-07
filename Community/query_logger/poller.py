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
# limitations under the License.

"""
Copyright BlueCat Networks, Inc. 2019
"""
__author__ = 'BlueCat Networks'

import datetime as dt
import resource
import sys
import signal
import time
from collections import OrderedDict


import requests
from pytz import timezone


class Poller(object):
    """
    Manages polling the Edge streaming endpoint and writing to the
    app and data loggers.
    """

    def __init__(self, cfg, app_logger, data_logger):
        self._applog = app_logger
        self._datalog = data_logger
        self._delimiter = cfg.get_value('datalog', 'delimeter')
        self._preamble = '{}|{}|{}|{}|'.format(
            cfg.get_value('datalog', 'leef_version'),
            cfg.get_value('datalog', 'vendor'),
            cfg.get_value('datalog', 'product'),
            cfg.get_value('datalog', 'version')
        )
        self._mapper = cfg.get_value('datalog', 'mapper')

    def _get_threats(self, threats):
        first = True
        threat_list = ''
        for threat in threats:
            if first:
                first = False
            else:
                threat_list += ','
            threat_list += threat['type']
        return threat_list

    def _get_threatIndicators(self, threats):
        first = True
        indicator_list = ''
        for thread in threats:
            for indicator in thread['indicators']:
                if first:
                    first = False
                else:
                    indicator_list += ','
                indicator_list += indicator
        return indicator_list

    def _get_query_kind(self, queryType):
        query_kind = 'other'
        if queryType == 'A' or queryType == "AAAA":
            query_kind = 'forward'
        elif queryType == 'PTR':
            query_kind = 'reverse'
        return query_kind

    def _get_query_status(self, query):
        query_status = 'unknown'
        if query['actionTaken'] == 'block':
            query_status = 'prevented'
        elif query['response'] == 'SERVFAIL':
            query_status = 'failed'
        else:
            query_status = 'succeeded'
        return query_status

    def _log_query(self, data, action):
        message = self._preamble + action + '|{}|'.format(self._delimiter) + data
        self._datalog.info(message)

    def _generate_log_message(self, message):
        values = sorted([(str(k) + "=" + str(v))
                         for k, v in iter(message.items())])
        return self._delimiter.join(values)

    def _process_edge_data(self, data):
        for query in data:
            record_id = query['recordId']
            message = OrderedDict()
            for siemattr in self._mapper:
                edgeattr = self._mapper[siemattr]
                if siemattr == 'devTime':
                    qtime = dt.datetime.utcfromtimestamp(int(query['time']) / 1000.0)
                    qtime = qtime.replace(tzinfo=timezone('UTC'))
                    message.update({siemattr: qtime.strftime('%d %b %Y %H:%M:%S %z')})
                    message.update({'devTimeFormat': 'MMM dd yyyy HH:mm:ss.SSS z'})
                elif siemattr == 'policy':
                    first = True
                    policy_list = ''
                    for policy in query['matchedPolicies']:
                        if first:
                            first = False
                        else:
                            policy_list += ','
                        policy_list += policy['name']
                    message.update({siemattr: policy_list})
                elif siemattr == 'threats':
                    message.update({siemattr: self._get_threats(query['threats'])})
                elif siemattr == 'threatIndicators':
                    message.update({siemattr: self._get_threatIndicators(query['threats'])})
                elif siemattr == 'rawData':
                    message.update({siemattr: query['query']})
                elif siemattr == 'queryKind':
                    message.update({siemattr: self._get_query_kind(query['queryType'])})
                elif siemattr == 'queryStatus':
                    message.update({siemattr: self._get_query_status(query)})
                elif edgeattr in query.keys():
                    message.update({siemattr: query[edgeattr]})
                else:
                    message.update({siemattr: 'Not in Log'})
            action = query['actionTaken']
            self._applog.debug(record_id)
            self._log_query(self._generate_log_message(message), action)

    def get_event_from_api(self, edge_api):
        data = edge_api.query_log_stream()
        if data is not None and 0 < len(data):
            self._applog.info('Processing %d events' % len(data))
            self._process_edge_data(data)
        else:
            self._applog.info('No events found')
