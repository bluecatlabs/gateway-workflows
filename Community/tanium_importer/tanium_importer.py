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
# Date: 2020-05-31
# Gateway Version: 20.3.1
# Description: Tanium Importer.py

import os
import sys
import json
import ipaddress

from datetime import datetime, timedelta
from dateutil import parser
from pytz import timezone
from threading import Lock

from bluecat import util
from bluecat.util import safe_str
from bluecat.entity import Entity
from bluecat.api_exception import BAMException, PortalException

from tanium.taniumapi import TaniumAPI

class TaniumImporterException(Exception): pass

class TaniumImporter(object):
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
                    cls._unique_instance._clients = []
                    cls._unique_instance._load()
        return cls._unique_instance

    def _load(self):
        with open(TaniumImporter._config_file) as f:
            self._config = json.load(f)

    def get_value(self, key):
        value = None
        with TaniumImporter._lock:
            if key in self._config.keys():
                value = self._config[key]
        return value

    def set_value(self, key, value):
        with TaniumImporter._lock:
            self._config[key] = value

    def get_clients(self):
        clients = []
        with TaniumImporter._lock:
            clients = self._clients
        return clients

    def set_clients(self, clients):
        with TaniumImporter._lock:
            self._clients = clients

    def clear_clients(self):
        with TaniumImporter._lock:
            self._clients = []

    def save(self):
        with TaniumImporter._lock:
            with open(TaniumImporter._config_file, 'w') as f:
                json.dump(self._config, f, indent=4)

    def _get_assignable_name(self, client):
        return client['name'] if client['name'] != '-' else ''

    def _convert_mac(self, tc_mac):
        mac_address = ''
        length = len(tc_mac)
        if tc_mac is not None:
            for i in range(length):
                mac_address += tc_mac[i].upper().replace(':', '-')
                if i + 1 < length:
                    mac_address += ', '
        return mac_address
        
    def _construct_tanium_url(self, tanium_api, client):
        return tanium_api.get_client_detail_url(self.get_value('server_addr'), client['id'])
        
    def _construct_linked_name(self, tanium_api, client):
        return "<a href='%s'  target='_blank'>%s</a>" % \
            (self._construct_tanium_url(tanium_api, client), client['name'])

    def _to_subnets_list(self, networks):
        subnets = []
        for subnet in networks.split(','):
            if subnet != '':
                subnets.append(subnet.strip())
        return subnets
        
    def _collect_clients(self, configuration, tanium_api, target_networks, include_discovery):
        retry_count = self.get_value('retry_count')
        interval = self.get_value('interval')
        clients = []
        subnets = self._to_subnets_list(target_networks)
        result = tanium_api.get_managed_assets(subnets, retry_count, interval)
        tanium_clients = result['clients']
        
        if include_discovery:
            result = tanium_api.get_unmanaged_assets(subnets, retry_count, interval)
            tanium_clients.extend(result['clients'])
        
        for tc in tanium_clients:
            client = {}
            client['managed'] = 'MANAGED' if tc['managed'] else 'UNKNOWN'
            client['id'] = tc['id']
            client['order'] = util.ip42int(tc['ip_address'])
            client['name'] = tc['computer_name']
            client['system'] = tc['manufacturer']
            
            if tc['os'] is not None and 0 < len(tc['os']):
                if 0 < len(client['system']):
                    client['system'] += ' - '
                client['system'] += tc['os']
                
            client['ipaddr'] = tc['ip_address']
            client['macaddr'] = self._convert_mac(tc['mac_address'])
            client['detail_link'] = ''
            client['linked_name'] = tc['computer_name']
            client['last_found'] = tc['last_found']
            
            client['state'] = 'UNKNOWN'
            clients.append(client)
            print(client)
        
        return clients

    def _collect_ip4_networks(self, configuration, ip4_networks, ipaddr):
        pack_address = util.ip42int(ipaddr)
        for ip4_network in ip4_networks:
            cidr = ip4_network.get_property('CIDR')
            network = ipaddress.IPv4Network(cidr)
            start_address = util.ip42int(str(network.network_address))
            end_address = util.ip42int(str(network.broadcast_address))
            if start_address <= pack_address <= end_address:
                return
                
        try:
            found = configuration.get_ip_range_by_ip(Entity.IP4Network, ipaddr)
            if found is not None:
                ip4_networks.append(found)
                
        except PortalException as e:
            print(safe_str(e))
            
    def _compare_clients(self, configuration, clients):
        ip4_networks = []
        include_matches = self.get_value('include_matches')
        include_ipam_only = self.get_value('include_ipam_only')
        
        for client in clients:
            self._collect_ip4_networks(configuration, ip4_networks, client['ipaddr'])
            
        for ip4_network in ip4_networks:
            ip4_addresses = ip4_network.get_children_of_type(Entity.IP4Address)
            for ip4_address in ip4_addresses:
                founds = [client for client in clients if client['ipaddr'] == ip4_address.get_address()]
                if 0 == len(founds):
                    if include_ipam_only == True and ip4_address.get_state() != 'DHCP_FREE':
                        new_client = {}
                        new_client['id'] = 'BlueCat_' + str(ip4_address.get_id())
                        new_client['network_id'] = ''
                        new_client['order'] = util.ip42int(ip4_address.get_address())
                        new_client['name'] = ip4_address.get_name()
                        new_client['system'] = ''
                        new_client['ipaddr'] = ip4_address.get_address()
                        macaddr = ip4_address.get_property('macAddress')
                        new_client['macaddr'] = macaddr if macaddr is not None else ''
                        new_client['detail_link'] = ''
                        new_client['linked_name'] = ip4_address.get_name()
                        new_client['last_found'] = '-'
                        new_client['state'] = 'RECLAIM'
                        clients.append(new_client)
                else:
                    macaddress = ip4_address.get_property('macAddress')
                    found = founds[0]
                    matched_macs = [mac for mac in found['macaddr'].split(',') if macaddress == mac.strip()]
                    print("found['mcaddr'] = ", found['macaddr'], ', maccaddress = ', macaddress )
                    
                    if 0 < len(matched_macs):
                        found['state'] = 'MATCH'
                        found['macaddr'] = matched_macs[0].strip()
                    else:
                        found['state'] = 'MISMATCH'
                    if include_matches == False and found['state'] == 'MATCH':
                        clients.remove(found)

    def _update_mac_by_client(self, configuration, client):
        mac_address = None
        assignalbe_name = self._get_assignable_name(client)
        try:
            mac_address = configuration.get_mac_address(client['macaddr'])
            if mac_address.get_name() is None and assignalbe_name != '':
                mac_address.set_name(assignalbe_name)
        except PortalException as e:
            mac_address = configuration.add_mac_address(client['macaddr'], assignalbe_name)
            
        mac_address.set_property('DetailLink', client['detail_link'])
        mac_address.set_property('System', client['system'])
        mac_address.set_property('ImportedSource', 'Tanium')
        mac_address.update()

    def _assigne_by_client(self, configuration, client):
        try:
            iprange = configuration.get_ip_range_by_ip('DHCP4Range', client['ipaddr'])
        except PortalException as e:
            properties='name=' + self._get_assignable_name(client)
            ipaddress = \
                configuration.assign_ip4_address(client['ipaddr'], \
                    client['macaddr'], '', 'MAKE_STATIC', properties=properties)
        self._update_mac_by_client(configuration, client)

    def _update_by_client(self, configuration, client):
        try:
            ipaddress = configuration.get_ip4_address(client['ipaddr'])
            assignalbe_name = self._get_assignable_name(client)
            if ipaddress.get_name() is None and assignalbe_name != '':
                ipaddress.set_name(assignalbe_name)
            ipaddress.set_property('macAddress', client['macaddr'])
            ipaddress.update()
        except PortalException as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % safe_str(e))
            
        self._update_mac_by_client(configuration, client)

    def _free_by_client(self, configuration, client):
        try:
            iprange = configuration.get_ip_range_by_ip('DHCP4Range', client['ipaddr'])
        except PortalException as e:
            try:
                ipaddress = configuration.get_ip4_address(client['ipaddr'])
                ipaddress.delete()
            except PortalException as e:
                if self._debug:
                    print('DEBUG: Exceptin <%s>' % safe_str(e))

    def collect_clients(self, configuration):
        succeed = False
        tanium_api = TaniumAPI(self.get_value('server_addr'), ignore_ssl_validation=True, debug=True)
        try:
            
            if tanium_api.login(self.get_value('user_id'), self.get_value('password')) == False:
                return succeed
                
            clients = self._collect_clients(configuration, tanium_api,
                                            self.get_value('target_networks'),
                                            self.get_value('include_discovery'))
                                            
            self._compare_clients(configuration, clients)
            clients.sort(key = lambda client: client['order'])
            self.set_clients(clients)
                
            tanium_api.logout()
        except Exception as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return succeed

    def import_clients(self, configuration):
        for client in self.get_clients():
            print('Importing %s[%s] ' % (client['name'], client['state']))
            if 'UNKNOWN' == client['state']:
                self._assigne_by_client(configuration, client)
            elif 'MISMATCH' == client['state']:
                self._update_by_client(configuration, client)
            elif 'MATCH' == client['state']:
                self._update_mac_by_client(configuration, client)
            elif 'RECLAIM' == client['state']:
                self._free_by_client(configuration, client)
        self.clear_clients()
        
