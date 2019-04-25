# Copyright 2018 BlueCat Networks. All rights reserved.

import os
import sys
import requests
import json

base_url = 'https://endpoints.office.com/'

class EndpointsException(Exception): pass

class EndpointsAPI(object):

    def __init__ (self, client_id, debug=False):
        self._client_id = client_id
        self._loaded = False
        self._service_areas = []
        self._endpoints = []
        self._debug = debug
        
    def validate_client_id(self):
        valid = False
        try:
            params = {'ClientRequestId': self._client_id}
            response = requests.get(base_url + 'version', params=params)
            if response.status_code == 200:
                valid = True
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return valid
        
    def _collect_service_areas(self):
        service_area_dict = {}
        
        for ep in self._endpoints:
            service_area = ep['serviceArea']
            if service_area not in service_area_dict:
                service_area_dict[service_area] = {
                    'name': service_area,
                    'display_name': ep['serviceAreaDisplayName'],
                    'check': True
                }
        self._service_areas = list(service_area_dict.values())
        
    def get_versions(self):
        versions = []
        try:
            params = {'ClientRequestId': self._client_id}
            response = requests.get(base_url + 'version', params=params)
            if response.status_code == 200:
                versions = response.json()
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return versions
        
    def get_current_version(self, instance):
        version = None
        try:
            params = {'ClientRequestId': self._client_id}
            response = requests.get(base_url + 'version/' + instance, params=params)
            if response.status_code == 200:
                contents = response.json()
                version = contents.get('latest')
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return version
        
    def _load_endpoints(self, instance):
        valid = False
        try:
            params = {'ClientRequestId': self._client_id}
            response = requests.get(base_url + 'endpoints/' + instance, params=params)
            if response.status_code == 200:
                self._endpoints = response.json()
                self._collect_service_areas()
                self._loaded = True
                valid = True
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return valid
        
    def get_service_areas(self, instance):
        if not self._loaded:
            self._load_endpoints(instance)
        return self._service_areas
        
    def get_endpoints(self, instance):
        if not self._loaded:
            self._load_endpoints(instance)
        return self._endpoints
        
