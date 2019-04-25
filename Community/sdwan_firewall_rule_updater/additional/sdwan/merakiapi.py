# Copyright 2018 BlueCat Networks. All rights reserved.

import os
import sys
import requests
import json


api_base = 'https://api.meraki.com/api'
api_url = {
    'get_organizations': api_base + '/v0/organizations',
    'get_config_templates': api_base + '/v0/organizations/{id}/configTemplates',
    'get_firewall_rules': api_base + '/v0/networks/{id}/l3FirewallRules',
    'update_firewall_rules': api_base + '/v0/networks/{id}/l3FirewallRules',
}

class MerakiException(Exception): pass

class MerakiAPI(object):

    def __init__ (self, api_key, debug=False):
        self._api_key = api_key
        self._headers = {'X-Cisco-Meraki-API-Key': api_key}
        self._debug = debug
        
    def validate_api_key(self):
        valid = False
        try:
            response = requests.get(api_url['get_organizations'], headers=self._headers)
            if response.status_code == 200:
                valid = True
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        except requests.exceptions.ConnectionError as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return valid
        
    def get_organizations(self):
        organizations = []
        try:
            response = requests.get(api_url['get_organizations'], headers=self._headers)
            if response.status_code == 200:
                organizations = response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise MerakiException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return organizations
        
    def get_organization(self, name):
        for org in self.get_organizations():
            if name == org['name']:
                return org
        return None
        
    def get_config_templates(self, id):
        templates = []
        try:
            response = requests.get(api_url['get_config_templates'].format(id=id), headers=self._headers)
            if response.status_code == 200:
                templates = response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise MerakiException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return templates
        
    def get_config_template(self, id, name):
        for template in self.get_config_templates(id):
            if name == template['name']:
                return template
        return None
        
    def get_firewall_rules(self, id):
        rules = []
        try:
            response = requests.get(api_url['get_firewall_rules'].format(id=id), headers=self._headers)
            if response.status_code == 200:
                rules = response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise MerakiException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return rules
        
    def create_allow_firewall_rule(self, domains, port, protocol, comments):
        rule = {}
        rule['protocol'] = protocol.lower()
        rule['destPort'] = port
        rule['destCidr'] = ','.join(domains)
        rule['comment'] = comments
        rule['policy'] = 'allow'
        rule['srcPort'] = 'Any'
        rule['srcCidr'] = 'Any'
        rule['syslogEnabled'] = False
        return rule
        
    def update_firewall_rules(self, id, rules):
        try:
            data = {}
            data['rules'] = rules
            data['syslogEnabled'] = True
            
            response = requests.put(api_url['update_firewall_rules'].format(id=id), json=data, headers=self._headers)
            if response.status_code == 200:
                return response.json()
            else:
                if self._debug:
                    print('DEBUG: failed response <%s>' % str(vars(response)))
                raise MerakiException(response)
        except requests.exceptions.RequestException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
                
