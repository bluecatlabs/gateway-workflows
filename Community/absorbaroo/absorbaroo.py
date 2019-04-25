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
# limitations under the License

import os
import sys
import datetime
import re
import pytz
import json
import hashlib
import functools
from threading import Lock
from apscheduler.schedulers.background import BackgroundScheduler

from o365.endpoints import EndpointsAPI
from dnsedge.edgeapi import EdgeAPI
from sdwan.merakiapi import MerakiAPI

class AbsorbarooException(Exception): pass

def _fqdn_reverse(x):
    xa = x.split('.')
    xa.reverse()
    return '.'.join(xa)

def _fqdn_cmp(x, y):
    xr = _fqdn_reverse(x)
    yr = _fqdn_reverse(y)
    if xr == yr:
        return 0
    elif xr < yr:
        return -1
    else:
        return 1

def _fqdn_normalize_for_edge(x):
    result = []
    xa = x.split('.')
    for xe in xa:
        if '*' in xe:
            continue
        result.append(xe)
    return '.'.join(result)

def _fqdn_normalize_for_meraki(dls):
    prv_domain = None
    new_dl = []
    for dl in dls:
        result = []
        xa = dl.split('.')
        for xe in xa:
            if '*' in xe:
                result.append('*')
            else:
                result.append(xe)
        new_domain = '.'.join(result)
        if prv_domain is None:
            pass
        elif prv_domain == new_domain:
            continue

        new_dl.append(new_domain)
        prv_domain = new_domain
    return new_dl

class Absorbaroo(object):
    _unique_instance = None
    _lock = Lock()
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
                    cls._unique_instance._load()
        return cls._unique_instance

    def _load(self):
        with open(Absorbaroo._config_file) as f:
            self._config = json.load(f)

    def get_value(self, key):
        value = None
        with Absorbaroo._lock:
            if key in self._config.keys():
                value = self._config[key]
        return value

    def set_value(self, key, value):
        with Absorbaroo._lock:
            self._config[key] = value

    def save(self):
        with Absorbaroo._lock:
            with open(Absorbaroo._config_file, 'w') as f:
                json.dump(self._config, f, indent=4)

    def _get_domainlist_id(self, edge_api, name):
        domainlists = edge_api.get_domainlists()
        for dl in domainlists:
            if name == dl['name']:
                return dl['id']
        return ''

    def _complie_domainlist(self, endpoints):
        domainlist = []
        for ep in endpoints:
            if 'urls' in ep.keys():
                domainlist.extend(ep['urls'])
        domainlist = list(set(domainlist))
        domainlist.sort(key=functools.cmp_to_key(_fqdn_cmp))

        compiled_domainlist = []
        previouse = None
        for dl in domainlist:
            dln = _fqdn_normalize_for_edge(dl)
            if previouse is None:
                pass
            elif previouse in dln:
                continue

            compiled_domainlist.append(dln)
            previouse = dln

        if self._debug:
            print('Sorted domains')
            print(compiled_domainlist)
        return compiled_domainlist

    def _create_domainlist_file(self, endpoints):
        domainlist = self._complie_domainlist(endpoints)
        csvfile = os.path.dirname(os.path.abspath(__file__)) + '/domainlist.txt'

        with open(csvfile, 'w') as f:
            for dl in domainlist:
                f.write(dl + '\n')

        return csvfile

    def _update_domainlist(self, edge_api, endpoints):
        succeed = False
        if edge_api.login(self.get_value('edge_username'), self.get_value('edge_password')):
            domainlist = self.get_value('edge_domainlist')
            if '' == domainlist['edge_id']:
                domainlist['edge_id'] = self._get_domainlist_id(edge_api, domainlist['name'])

            if '' != domainlist['edge_id']:
                cvsfile = self._create_domainlist_file(endpoints)
                edge_api.update_domainlist(domainlist['edge_id'], cvsfile)
                succeed = True

            edge_api.logout()
        return succeed

    def _get_network_id(self, meraki_api):
        network_id = None
        organization = meraki_api.get_organization(self.get_value('sdwan_orgname'))
        if organization is not None:
            template = meraki_api.get_config_template(organization['id'], self.get_value('sdwan_tmpname'))
            if template is not None:
                network_id = template['id']
        return network_id

    def _update_firewall_rules(self, meraki_api, endpoints):
        succeed = False

        new_rules = []
        delimiter_rule = None
        delimiter_key = self.get_value('sdwan_delimit_key')

        network_id = self._get_network_id(meraki_api)
        rules = meraki_api.get_firewall_rules(network_id)

        # Skip Delimiter Rule and Exist DNS Edge Domainlist Firewall Rules.
        for rule in rules:
            comment = rule['comment']
            if delimiter_key in comment:
                delimiter_rule = rule
                continue
            elif 'Default rule' in comment or 'Office365' in comment:
                continue
            else:
                new_rules.append(rule)

        #Add Office 365 Firewall Rues.
        for ep in endpoints:
            if 'urls' in ep.keys():
                destCidr = _fqdn_normalize_for_meraki(ep['urls'])
                port = ep['tcpPorts']
                protocol = 'Any'
                comments = 'Office365 (id:{id} {area})'.format(id=ep['id'],area=ep['serviceArea'])
                new_rule = meraki_api.create_allow_firewall_rule(destCidr, port, protocol, comments)
                new_rules.append(new_rule)

        if delimiter_rule is not None:
            new_rules.append(delimiter_rule)

        if self._debug:
            print('Dumping New Rules.......')
            debug_file = os.path.dirname(os.path.abspath(__file__)) + '/firewall_rules.txt'
            with open(debug_file, 'w') as f:
                f.write(str(json.dumps(new_rules, indent=2)))

        meraki_api.update_firewall_rules(network_id, new_rules)
        succeed = True
        return succeed

    def _include(self, serviceArea):
        for sa in self.get_value('o365_service_areas'):
            if serviceArea == sa['name']:
                return ("True" == sa['check'])
        return False

    def _get_endpoints(self, ep_api):
        endpoints = []
        for ep in ep_api.get_endpoints(self.get_value('o365_instance')):
            if self._include(ep['serviceArea']):
                endpoints.append(ep)
        return endpoints

    def synchronize_endpoints(self):
        if self._debug:
            print('Synchronize Endpoints is called....')
        ep_api = EndpointsAPI(self.get_value('o365_client_id'), debug=True)
        edge_api = EdgeAPI(self.get_value('edge_url'), debug=True)
        meraki_api = MerakiAPI(self.get_value('sdwan_key'), debug=True)

        # Checking Office 365 endpoints
        if not ep_api.validate_client_id():
            return False
        latest_version = ep_api.get_current_version(self.get_value('o365_instance'))
        if self._debug:
            print('Now Checking Version....<%s> vs. <%s>' % (self.get_value('current_version'), latest_version))
        if self.get_value('current_version') == latest_version:
            return True
        endpoints = self._get_endpoints(ep_api)

        # Checking DNS Edge CI
        if not edge_api.validate_edgeurl():
            return False

        if self._debug:
            print('Now Updating both Domainlist....')

        succeed = False
        if self._update_domainlist(edge_api, endpoints):
            #Checking Meraki
            if meraki_api.validate_api_key():
                self._update_firewall_rules(meraki_api, endpoints)
            self.set_value('current_version', latest_version)
            timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f UTC")
            self.set_value('last_execution', timestamp)
            self.save()
            succeed = True
        return succeed

    def force_synchronize_endpoints(self):
        ep_api = EndpointsAPI(self.get_value('o365_client_id'), debug=True)
        edge_api = EdgeAPI(self.get_value('edge_url'), debug=True)
        meraki_api = MerakiAPI(self.get_value('sdwan_key'), debug=True)

        # Checking Office 365 endpoints
        if not ep_api.validate_client_id():
            return False
        latest_version = ep_api.get_current_version(self.get_value('o365_instance'))
        endpoints = self._get_endpoints(ep_api)

        # Checking DNS Edge CI
        if not edge_api.validate_edgeurl():
            return False

        succeed = False
        if self._update_domainlist(edge_api, endpoints):
            #Checking Meraki
            if meraki_api.validate_api_key():
                self._update_firewall_rules(meraki_api, endpoints)
            self.set_value('current_version', latest_version)
            timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f UTC")
            self.set_value('last_execution', timestamp)
            self.save()
            succeed = True
        return succeed

    def clear_endpoints(self):
        edge_api = EdgeAPI(self.get_value('edge_url'), debug=True)
        meraki_api = MerakiAPI(self.get_value('sdwan_key'), debug=True)
        endpoints = []

        # Checking DNS Edge CI
        if not edge_api.validate_edgeurl():
            return False

        succeed = False
        if self._update_domainlist(edge_api, endpoints):
            #Checking Meraki
            if meraki_api.validate_api_key():
                self._update_firewall_rules(meraki_api, endpoints)
            self.set_value('current_version', "")
            self.set_value('last_execution', "")
            self.save()
            succeed = True
        return succeed

    def register_synchronize_job(self):
        succeed = False
        try:
            interval = self.get_value('execution_interval')
            if self._scheduler is None:
                self._scheduler = BackgroundScheduler(daemon=True, timezone=pytz.utc)
                self._scheduler.start()

            if self._job is not None:
                self._job.remove()
                self._job = None

            if interval is not None and 0 < interval:
                if self._debug:
                    print('Now Registering Synchronize Endpoints...')
                self._job = \
                    self._scheduler.add_job(self.synchronize_endpoints, 'interval', seconds=interval)
                succeed = True

        except Exception as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return succeed
#
# Followings are code that should be executed when this module is loaded.
#

absorbaroo = Absorbaroo.get_instance(debug=True)
print("Absorbaroo is loaded.......")
if absorbaroo.register_synchronize_job():
    print("Synchronization Job is registered.......")
