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
# By: Akira Goto (agoto@bluecatnetworks.com)
# Date: 2020-03-301
# Gateway Version: 20.12.1
# Description: CISCO Meraki Importer.py

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

from sdwan.merakiapi import MerakiAPI

class MerakiImporterException(Exception): pass

class MerakiImporter(object):
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
        with open(MerakiImporter._config_file) as f:
            self._config = json.load(f)

    def get_value(self, key):
        value = None
        with MerakiImporter._lock:
            if key in self._config.keys():
                value = self._config[key]
        return value

    def set_value(self, key, value):
        with MerakiImporter._lock:
            self._config[key] = value

    def get_clients(self):
        clients = []
        with MerakiImporter._lock:
            clients = self._clients
        return clients

    def set_clients(self, clients):
        with MerakiImporter._lock:
            self._clients = clients

    def clear_clients(self):
        with MerakiImporter._lock:
            self._clients = []

    def save(self):
        with MerakiImporter._lock:
            with open(MerakiImporter._config_file, 'w') as f:
                json.dump(self._config, f, indent=4)

    def _get_assignable_name(self, client):
        return client['name'] if client['name'] != '-' else ''

    def _convert_mac(self, mc_mac):
        mac_address = ''
        if mc_mac is not None:
            mac_address = mc_mac.replace(':', '-').upper()
        return mac_address
        
    def _construct_meraki_url(self, meraki_api, client):
        return meraki_api.get_client_detail_url(self.get_value('dashboard_url'), client['id'])
        
    def _construct_linked_name(self, meraki_api, client):
        return "<a href='%s'  target='_blank'>%s</a>" % \
            (self._construct_meraki_url(meraki_api, client), client['name'])

    def _compare_client(self, configuration, ipaddr, macaddr):
        state = 'MISMATCH'
        try:
            ipaddress = configuration.get_ip4_address(ipaddr)
            macaddress = ipaddress.get_property('macAddress')
            if macaddress is not None:
                macaddress = macaddress.replace('-', ':')
                if macaddr == macaddress:
                    state = 'MATCH'
        except PortalException as e:
            state = 'UNKNOWN'
        except Exception as e:
            if self._debug:
                print('DEBUG: Exceptin <%s>' % str(e))
        return state
    
    def _collect_clients(self, configuration, meraki_api, network_id):
        clients = []
        now = datetime.now()
        meraki_clients = meraki_api.get_clients(network_id)
        
        for mc in meraki_clients:
            client = {}
            client['id'] = mc['id']
            client['network_id'] = network_id
            client['order'] = util.ip42int(mc['ip'])
            client['name'] = mc['description'] if mc['description'] is not None else '-'
            client['system'] = mc['manufacturer']  if mc['manufacturer'] is not None else ''
            
            if mc['os'] is not None and 0 < len(mc['os']):
                if 0 < len(client['system']):
                    client['system'] += ' - '
                client['system'] += mc['os']
                
            client['ipaddr'] = mc['ip']
            client['macaddr'] = self._convert_mac(mc['mac'])
            client['detail_link'] = self._construct_meraki_url(meraki_api, client)
            client['linked_name'] = self._construct_linked_name(meraki_api, client)
            
            client['last_found'] = mc['lastSeen']
            lastfound = parser.parse(mc['lastSeen'])
            lastfound = lastfound.replace(tzinfo=None)
            if (now - lastfound) > timedelta(days=30):
                client['state'] = 'RECLAIM'
            else:
                client['state'] = 'UNKNOWN'
                
            clients.append(client)
        clients.sort(key = lambda client: client['order'])
        
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
                    found['state'] = 'MATCH' if found['macaddr'] == macaddress else 'MISMATCH'
                    if include_matches == False and found['state'] == 'MATCH':
                        clients.remove(found)
                    
        clients.sort(key = lambda client: client['order'])
        
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
        mac_address.set_property('ImportedSource', 'Meraki')
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
        try:
            meraki_api = MerakiAPI(self.get_value('api_key'), debug=True)
            if not meraki_api.validate_api_key():
                return succeed
                
            organization = meraki_api.get_organization(self.get_value('org_name'))
            if organization is None:
                return succeed
                
            network = meraki_api.get_network(organization['id'], self.get_value('network_name'))
            if (network is not None) and (network['id'] != ''):
                clients = self._collect_clients(configuration, meraki_api, network['id'])
                self._compare_clients(configuration, clients)
                self.set_clients(clients)
                
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
        
