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
# Date: 2019-10-30
# Gateway Version: 20.12.1
# Description: BlueCat Gateway module for Fixpoint Kompira Cloud Sonar API calls

import os
import sys
import requests
import json


LIMIT_NODES = 30

api_url = {
    'get_networks': '/api/apps/sonar/networks',
    'get_network': '/api/apps/sonar/networks/{id}',
    'get_nodes': '/api/apps/sonar/networks/{id}/managed-nodes',
    'get_node_detail': '/apps/sonar/networks/{network_id}/managed-nodes/{node_id}/'
}

class SonarException(Exception): pass

class SonarAPI(object):

    def __init__ (self, instance, api_key, debug=False):
        self._instance = instance
        self._api_key = api_key
        self._headers = {'X-Authorization': 'Token ' + api_key}
        self._debug = debug

    def _get_url(self, key):
        return self._instance + api_url[key]

    def validate_api_key(self):
        valid = False
        try:
            response = requests.get(self._get_url('get_networks'), headers=self._headers)
            if response.status_code == 200:
                valid = True
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return valid

    def get_networks(self):
        networks = []
        try:
            response = requests.get(self._get_url('get_networks'), headers=self._headers)
            if response.status_code == 200:
                networks = response.json()['items']
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise SonarException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return networks

    def get_network(self, id):
        node = None
        try:
            response = requests.get(self._get_url('get_network').format(id=id), headers=self._headers)
            if response.status_code == 200:
                node = response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise SonarException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return node

    def get_network_by_name(self, name):
        for network in self.get_networks():
            if name == network['displayName']:
                return network
        return None

    def get_nodes(self, id):
        nodes = []
        offset = 0
        while True:
            try:
                params = {'offset': offset, 'limit': 30, 'sort': 'managedNodeId'}
                response = requests.get(self._get_url('get_nodes').format(id=id), headers=self._headers, params=params)
                if response.status_code == 200:
                    items = response.json()['items']
                else:
                    if self._debug:
                        print('DEBUG: failed response <%s>' % str(vars(response)))
                    raise SonarException(response)
                nodes.extend(items)
                if len(items) < 30:
                    break
                offset += 30
            except requests.exceptions.RequestException as e:
                if self._debug:
                    print('DEBUG: Exceptin <%s>' % str(e))

        return nodes

    def get_node_detail_url(self, network_id, node_id):
        return self._get_url('get_node_detail').format(network_id=network_id, node_id=node_id)
