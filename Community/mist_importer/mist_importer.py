# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2019-10-30
# Gateway Version: 19.8.1
# Description: Juniper Mist Importer.py

import os
import sys
import json
import ipaddress

from datetime import datetime, timedelta
from dateutil import parser
from threading import Lock

from bluecat import util
from bluecat.util import safe_str
from bluecat.entity import Entity
from bluecat.api_exception import BAMException, PortalException

from mist.mistapi import MistAPI

class MistImporterException(Exception): pass

class MistImporter(object):
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
        with open(MistImporter._config_file) as f:
            self._config = json.load(f)

    def get_value(self, key):
        value = None
        with MistImporter._lock:
            if key in self._config.keys():
                value = self._config[key]
        return value

    def set_value(self, key, value):
        with MistImporter._lock:
            self._config[key] = value

    def get_clients(self):
        clients = []
        with MistImporter._lock:
            clients = self._clients
        return clients

    def set_clients(self, clients):
        with MistImporter._lock:
            self._clients = clients

    def clear_clients(self):
        with MistImporter._lock:
            self._clients = []

    def save(self):
        with MistImporter._lock:
            with open(MistImporter._config_file, 'w') as f:
                json.dump(self._config, f, indent=4)

    def _get_assignable_name(self, client):
        assignalbe_name = ''
        try:
            ipaddress.IPv4Address(client['name'])
        except ipaddress.AddressValueError:
            assignalbe_name = client['name']
        return assignalbe_name

    def _convert_mac(self, mc_mac):
        mac_address = ''
        if len(mc_mac) == 12:
            mac_address = mc_mac[0:2] + '-' + mc_mac[2:4] + '-' + mc_mac[4:6] + '-' + \
                mc_mac[6:8] + '-' + mc_mac[8:10] + '-' + mc_mac[10:12]
            mac_address = mac_address.upper()
        return mac_address
        
    def _construct_mist_url(self, mist_api, client):
        return mist_api.get_client_detail_url(client['site_id'], client['id'])
        
    def _construct_linked_name(self, mist_api, client):
        return "<a href='%s'  target='_blank'>%s</a>" % \
            (self._construct_mist_url(mist_api, client), client['name'])

    def _collect_clients(self, configuration, mist_api, site_id):
        clients = []
        now = datetime.now()
        mist_clients = mist_api.get_clients(site_id)
        
        for mc in mist_clients:
            client = {}
            if self._debug:
                print('mc:', mc)
            client['id'] = mc['_id']
            client['site_id'] = mc['site_id']
            client['order'] = util.ip42int(mc['ip'])
            client['name'] = mc['hostname'] if 'hostname' in mc.keys() else ''
            client['system'] = mc['manufacture'] if mc['manufacture'] != 'Unknown' else ''
            
            if mc['family'] is not None and 0 < len(mc['family']):
                if 0 < len(client['system']):
                    client['system'] += ' - '
                client['system'] += mc['family']
                
            if mc['os'] is not None and 0 < len(mc['os']):
                if 0 < len(client['system']):
                    client['system'] += ' ' if '-' in client['system'] else ' - '
                client['system'] += mc['os']
                
            client['ipaddr'] = mc['ip']
            client['macaddr'] = self._convert_mac(mc['mac'])
            client['detail_link'] = self._construct_mist_url(mist_api, client)
            client['linked_name'] = self._construct_linked_name(mist_api, client)
            
            lastfound = datetime.fromtimestamp(mc['last_seen'])
            lastfound = lastfound.replace(tzinfo=None)
            client['last_found'] = lastfound.strftime('%Y-%m-%dT%H:%M:%S')
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
                        new_client['id'] = ''
                        new_client['site_id'] = ''
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
        mac_address.set_property('ImportedSource', 'Mist')
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
            mist_api = MistAPI(self.get_value('org_id'), self.get_value('api_token'), debug=True)
            if not mist_api.validate_api_key():
                return succeed
                
            site = mist_api.get_site_by_name(self.get_value('site_name'))
            if (site is not None) and (site['id'] != ''):
                clients = self._collect_clients(configuration, mist_api, site['id'])
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
        
