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
# Date: 2019-12-20
# Gateway Version: 18.10.2 and higher
# Description: BlueCat Gateway module for DNS Edge API calls

import os
import sys
import requests
import json


api_url = {
    'get_token': '/v1/api/authentication/token',
    'logout': '----Removed-----',
    'tos': '/v1/api/tos',
    'get_domainlists': '/v1/api/list/dns',
    'get_domainlist': '/v1/api/list/dns/{id}',
    'update_domainlist': '/v1/api/list/dns/{id}/attachfile',
    
    'get_policies': '/v5/api/policies',
    'get_policy': '/v5/api/policies/{id}',
    'update_policy': '/v5/api/policies/{id}',
    
    'get_sites': '/v3/api/sites',
    'get_service_points': '/v1/api/servicePoints',
    
    'query_log_stream': '/v2/api/customer/dnsQueryLog/stream',
    
    'get_service_point_status': ':80/v1/status/spDiagnostics'
}

class EdgeException(Exception): pass

class EdgeAPI(object):

    def __init__ (self, edgeurl, debug=False):
        self._edgeurl = edgeurl
        self._headers = {'Authorization': 'Bearer '}
        self._token = ''
        self._etag = ''
        self._debug = debug
        
    def validate_edgeurl(self):
        valid = False
        try:
            headers = {'Authorization': 'Bearer '}
            response = requests.get(self._edgeurl + api_url['tos'], headers=headers)
            if response.status_code == 200:
                if 'timestamp' in response.json():
                    valid = True
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return valid
        
    def login(self, client_id, secret):
        success = False
        try:
            body = { 
                'grantType': 'ClientCredentials',
                'clientCredentials': {
                    'clientId': client_id,
                    'clientSecret': secret
                }
            }
            headers = { 'Content-type': 'application/json' }
            response = requests.post(self._edgeurl + api_url['get_token'], json=body, headers=headers)
            if response.status_code == 200:
                result = response.json()
                self._headers =  {'Authorization': 'Bearer ' + result['accessToken']}
                success = True
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return success
        
    def logout(self):
        # No Longer Needed to call logout.
        pass
#         try:
#             response = requests.post(self._edgeurl + api_url['logout'], headers=self._headers)
#         except requests.exceptions.RequestException as e:
#             if self._debug:
#                 print('DEBUG: Exceptin <%s>' % str(e))
            
    def set_token(self, token):
        self._token = token
        self._etag = ''
        
    def get_domainlists(self):
        domainlists = []
        try:
            response = requests.get(self._edgeurl + api_url['get_domainlists'], headers=self._headers)
            if response.status_code == 200:
                domainlists = response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise EdgeException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return domainlists
        
    def get_domainlist(self, id):
        domainlist = []
        try:
            response = requests.get(self._edgeurl + api_url['get_domainlist'].format(id=id), headers=self._headers)
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                domainlist = content.splitlines()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise EdgeException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return domainlist
        
    def update_domainlist(self, id, csvfile):
        dict = {'file':(csvfile, open(csvfile, 'rb'), 'text/plain')}
        try:
            response = requests.post(self._edgeurl + api_url['update_domainlist'].format(id=id), files=dict, headers=self._headers)
            if response.status_code == 200:
                return response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise EdgeException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
                
    def get_policies(self):
        policies = []
        try:
            response = requests.get(self._edgeurl + api_url['get_policies'], headers=self._headers)
            if response.status_code == 200:
                policies = response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise EdgeException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return policies
        
    def get_policy_by_name(self, name):
        policy = None
        try:
            policies = self.get_policies()
            for p in policies:
                if name == p['name']:
                    policy = p
                    break
        except Exception as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
                
        return policy
        
    def get_policy(self, id):
        policy = {}
        try:
            response = requests.get(self._edgeurl + api_url['get_policy'].format(id=id), headers=self._headers)
            if response.status_code == 200:
                policy = response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise EdgeException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return policy
        
    def update_policy(self, id, policy):
        success = False
        try:
            response = requests.put(self._edgeurl + api_url['update_policy'].format(id=id), \
                json=policy, headers=self._headers)
            if response.status_code == 200 or response.status_code == 204:
                success = True
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise EdgeException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return success
        
    def get_sites(self):
        sites = []
        try:
            response = requests.get(self._edgeurl + api_url['get_sites'], headers=self._headers)
            if response.status_code == 200:
                sites = response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise EdgeException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return sites
        
    def get_service_points(self):
        service_points = []
        try:
            response = requests.get(self._edgeurl + api_url['get_service_points'], headers=self._headers)
            if response.status_code == 200:
                service_points = response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise EdgeException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return service_points
        
    def query_log_stream(self):
        headers = {'Authorization': 'Basic ' + self._token, 'ETag': self._etag}
        results = None
        try:
            response = requests.get(self._edgeurl + api_url['query_log_stream'], headers=headers)
            if response.status_code == 200:
                results = response.json()
                if 'ETag' in response.headers.keys() and response.headers['ETag'] is not None:
                    self._etag = response.headers['ETag']
                return results
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise EdgeException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return results
        
    def get_service_point_status_url(self, sp_address):
        return 'http://' + sp_address + api_url['get_service_point_status']
        
    def get_service_point_status(self, sp_address, timeout=1):
        status = None
        try:
            response = requests.get('http://' + sp_address + api_url['get_service_point_status'], timeout=timeout)
            if response.status_code == 200:
                status = response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectTimeout as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return status
        

