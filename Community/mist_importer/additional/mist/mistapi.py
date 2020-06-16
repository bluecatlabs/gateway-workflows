# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
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
# Gateway Version: 19.8.1 or greater
# Description: BlueCat Gateway module for Juniper Mist API calls

import os
import sys
import requests
import json


console_base_url = 'https://manage.mist.com/admin'
api_base_url = 'https://api.mist.com'

api_url = {
    'get_self': '/api/v1/self',
    'get_sites': '/api/v1/orgs/{id}/sites',
    'get_client_stats': '/api/v1/sites/{id}/stats/clients',
    'get_client_detail': '/?org_id={org_id}#!clients/detail/{client_id}/{site_id}'
}

class MistException(Exception): pass

class MistAPI(object):

    def __init__ (self, org_id, api_key, debug=False):
        self._org_id = org_id
        self._api_key = api_key
        self._headers = {'Authorization': 'Token ' + api_key}
        self._debug = debug
        
    def _get_url(self, key):
        return api_base_url + api_url[key]
        
    def validate_api_key(self):
        valid = False
        try:
            response = requests.get(self._get_url('get_self'), headers=self._headers)
            if response.status_code == 200:
                valid = True
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return valid
        
    def get_self(self):
        ret = None
        try:
            response = requests.get(self._get_url('get_self'), headers=self._headers)
            if response.status_code == 200:
                ret = response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise MistException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return ret
        
    def get_sites(self):
        sites = None
        try:
            response = requests.get(self._get_url('get_sites').format(id=self._org_id), headers=self._headers)
            if response.status_code == 200:
                sites = response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise MistException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return sites
        
    def get_site_by_name(self, name):
        for site in self.get_sites():
            if name == site['name']:
                return site
        return None
        
    def get_clients(self, id):
        clients = []
        try:
            response = requests.get(self._get_url('get_client_stats').format(id=id), headers=self._headers)
            if response.status_code == 200:
                clients = response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise MistException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return clients
        
    def get_client_detail_url(self, site_id, client_id):
        url = console_base_url + \
            api_url['get_client_detail'].format(org_id=self._org_id, client_id=client_id, site_id=site_id)
        return url
        
