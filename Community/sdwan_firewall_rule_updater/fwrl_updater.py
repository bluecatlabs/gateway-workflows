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
# By: Akira Goto (agoto@bluecatnetworks.com)
# Date: 2019-08-28
# Gateway Version: 19.5.1
# Description: SDWAN Firewall Rule Updater fwrl_updater.py

import os
import sys
import datetime
import pytz
import json
import hashlib
from threading import Lock
from apscheduler.schedulers.background import BackgroundScheduler

from dnsedge.edgeapi import EdgeAPI
from sdwan.merakiapi import MerakiAPI

class FWRLUpdaterException(Exception): pass


class FWRLUpdater(object):
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
        with open(FWRLUpdater._config_file) as f:
            self._config = json.load(f)

    def get_value(self, key):
        value = None
        with FWRLUpdater._lock:
            if key in self._config.keys():
                value = self._config[key]
        return value

    def set_value(self, key, value):
        with FWRLUpdater._lock:
            self._config[key] = value

    def save(self):
        with FWRLUpdater._lock:
            with open(FWRLUpdater._config_file, 'w') as f:
                json.dump(self._config, f, indent=4)

    def _get_domainlist_id(self, name, domainlists):
        for domainlist in domainlists:
            if name == domainlist['name']:
                return domainlist['id']
        return ''

    def _update_domainlist_ids(self, edge_api):
        domainlists = edge_api.get_domainlists()
        for edge_domainlist in self.get_value('edge_domainlists'):
            id = self._get_domainlist_id(edge_domainlist['name'], domainlists)
            if (id != '') and (id != edge_domainlist['edge_id']):
                edge_domainlist['edge_id'] = id
                edge_domainlist['hash_value'] = ''

    def _updates_domainlists(self, edge_api, domainlists):
        result = False

        for edge_domainlist in self.get_value('edge_domainlists'):
            if edge_domainlist['edge_id'] == '':
                continue

            domainlist = edge_api.get_domainlist(edge_domainlist['edge_id'])
            domainlists[edge_domainlist['name']] = domainlist
            hash_value = hashlib.md5(str(domainlist).encode('utf-8')).hexdigest()
            if hash_value != edge_domainlist['hash_value']:
                result = True
                edge_domainlist['hash_value'] = hash_value
        return result

    def _get_network_id(self, meraki_api):
        network_id = None
        organization = meraki_api.get_organization(self.get_value('sdwan_orgname'))
        if organization is not None:
            template = meraki_api.get_config_template(organization['id'], self.get_value('sdwan_tmpname'))
            if template is not None:
                network_id = template['id']
        return network_id

    def _convert_dls2destCidr(self, edge_dl, dls):
        destCidr = []
        for dl in dls:
            domains = dl.split('.')
            last = len(domains) - 1
            if '' == domains[last]:
                del domains[last]
            if edge_dl['fqdn'] != "True":
                domains.insert(0, '*')
            destCidr.append('.'.join(domains))
        return destCidr

    def _update_firewall_rules_by_dls(self, meraki_api, rules, domainlists):
        new_rules = []
        delimiter_rule = None
        delimiter_key = self.get_value('sdwan_delimit_key')

        # Skip Delimiter Rule and Exist DNS Edge Domainlist Firewall Rules.
        for rule in rules:
            comment = rule['comment']
            if delimiter_key in comment:
                delimiter_rule = rule
                continue
            elif 'Default rule' in comment or 'DNS Edge Domainlist' in comment:
                continue
            else:
                new_rules.append(rule)

        # Add DNS Edge Domainlist Firewall Rules.
        for edge_dl in self.get_value('edge_domainlists'):
            dl_name = edge_dl['name']
            if dl_name in domainlists.keys():
                destCidr = self._convert_dls2destCidr(edge_dl, domainlists[dl_name])
                port = edge_dl['port']
                protocol = edge_dl['protocol']
                comments = 'DNS Edge Domainlist (' +  dl_name + ')'
                new_rule = meraki_api.create_allow_firewall_rule(destCidr, port, protocol, comments)
                new_rules.append(new_rule)

        if delimiter_rule is not None:
            new_rules.append(delimiter_rule)

        if self._debug:
            print('Printing New Rules.......')
            print(new_rules)
        return new_rules

    def synchronize_domainlists(self):
        edge_api = EdgeAPI(self.get_value('edge_url'), debug=self._debug)
        meraki_api = MerakiAPI(self.get_value('sdwan_key'), debug=self._debug)

        if not edge_api.validate_edgeurl() or not meraki_api.validate_api_key():
            return False

        succeed = False
        if edge_api.login(self.get_value('edge_client_id'), self.get_value('edge_secret')):
            self._update_domainlist_ids(edge_api)
            domainlists = {}
            if self._debug:
                print("Now Checking Updated Domainlists....")

            if self._updates_domainlists(edge_api, domainlists):
                if self._debug:
                    print("Now Synchronizing....")

                network_id = self._get_network_id(meraki_api)
                if network_id is not None:
                    rules = meraki_api.get_firewall_rules(network_id)
                    new_rules = self._update_firewall_rules_by_dls(meraki_api, rules, domainlists)
                    meraki_api.update_firewall_rules(network_id, new_rules)
                    timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f UTC")
                    self.set_value('last_execution', timestamp)
                    self.save()
                    succeed = True
                if self._debug:
                    print("Now Synchronization is complted")
            edge_api.logout()

        return succeed

    def force_synchronize_domainlists(self):
        edge_api = EdgeAPI(self.get_value('edge_url'), debug=True)
        meraki_api = MerakiAPI(self.get_value('sdwan_key'), debug=True)

        if not edge_api.validate_edgeurl() or not meraki_api.validate_api_key():
            return False

        succeed = False
        if edge_api.login(self.get_value('edge_client_id'), self.get_value('edge_secret')):
            self._update_domainlist_ids(edge_api)
            domainlists = {}
            self._updates_domainlists(edge_api, domainlists)
            if self._debug:
                print("Now Synhronizing....")

            network_id = self._get_network_id(meraki_api)
            if network_id is not None:
                rules = meraki_api.get_firewall_rules(network_id)
                new_rules = self._update_firewall_rules_by_dls(meraki_api, rules, domainlists)
                meraki_api.update_firewall_rules(network_id, new_rules)
                timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f UTC")
                self.set_value('last_execution', timestamp)
                self.save()
                succeed = True
            edge_api.logout()

        return succeed

    def _clear_domainlists(self):
        for edge_domainlist in self.get_value('edge_domainlists'):
            edge_domainlist['edge_id'] = ''
            edge_domainlist['hash_value'] = ''

    def clear_domainlists(self):
        meraki_api = MerakiAPI(self.get_value('sdwan_key'), debug=True)

        if not meraki_api.validate_api_key():
            return False

        succeed = False
        domainlists = {}
        if self._debug:
            print("Now Clearing....")

        self._clear_domainlists()
        network_id = self._get_network_id(meraki_api)
        if network_id is not None:
            rules = meraki_api.get_firewall_rules(network_id)
            new_rules = self._update_firewall_rules_by_dls(meraki_api, rules, domainlists)
            meraki_api.update_firewall_rules(network_id, new_rules)
        self.set_value('last_execution', "")
        self.save()
        return True

    def register_synchronize_job(self):
        succeed = False
        try:
            interval = self.get_value('execution_interval')
            edge_api = EdgeAPI(self.get_value('edge_url'), debug=True)
            meraki_api = MerakiAPI(self.get_value('sdwan_key'), debug=True)
            if not edge_api.validate_edgeurl() or \
                not meraki_api.validate_api_key():
                return succeed

            if self._scheduler is None:
                self._scheduler = BackgroundScheduler(daemon=True, timezone=pytz.utc)
                self._scheduler.start()

            if self._job is not None:
                self._job.remove()
                self._job = None

            if interval is not None and 0 < interval:
                self._job = \
                    self._scheduler.add_job(self.synchronize_domainlists, 'interval', seconds=interval)
                succeed = True

        except Exception as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return succeed
#
# Followings are code that should be executed when this module is loaded.
#

updater = FWRLUpdater.get_instance(debug=True)
print("FWRLUpdater is loaded.......")
if updater.register_synchronize_job():
    print("Synchronization Job is registered.......")
