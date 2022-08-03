# Copyright 2022 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2022-06-30
# Description:
#   Calculate DHCP Range Usage specified BAM, network_id.

import copy
import csv
import ipaddress
import psycopg2
import traceback

from bluecat_libraries.address_manager.api import Client
from bluecat_libraries.address_manager.constants import IPAddressState
from bluecat_libraries.address_manager.constants import ObjectType

MAX_COUNT = 300000

def get_range(entity):
    range = ''
    props = entity['properties']
    if 'CIDR' in props.keys():
        range = props['CIDR']
        if '-' in range:
            ranges = range.split('-')
            range = '{start}-{end}'.format(start=ranges[0].strip(), end=ranges[1].strip())
    return range
    
def is_inside_dhcp_range(dhcp_ranges, ip_address):
    result = False
    ip_addr = int(ipaddress.ip_address(ip_address))
    for dhcp_range in dhcp_ranges:
        if dhcp_range['start_ip'] <= ip_addr and ip_addr <= dhcp_range['end_ip']:
            result = True
            break
            
    return result
    
    
def get_exclusion_ranges(connector, range_id):
    ranges = []
    with connector.cursor() as cursor:
        sql = "SELECT mv.text " \
            "FROM public.metadata_field mf," \
                "public.metadata_value mv " \
            f"WHERE mf.name = 'exclusions' AND mf.id = mv.field_id AND mv.owner_id = {range_id}"
        
        cursor.execute(sql)
        result = cursor.fetchall()
        if 0 < len(result):
            for range in result[0][0].split('|'):
                if range != '':
                    values = range.split(',')
                    ranges.append((int(values[0]), int(values[1])))
    return ranges

def normalize_range(connector, dhcp_range):
    ranges = []
    props = dhcp_range['properties']
    dhcp_range['start_ip'] = int(ipaddress.ip_address(props['start']))
    dhcp_range['end_ip'] = int(ipaddress.ip_address(props['end']))
    exclusion_ranges = get_exclusion_ranges(connector, dhcp_range['id'])
    exclusion_ranges.sort(key = lambda node: node[0])
    
    if 0 < len(exclusion_ranges):
        start_ip = dhcp_range['start_ip']
        end_ip = dhcp_range['end_ip']
        rest_dhcp_range = copy.deepcopy(dhcp_range)
        for exclusion_range in exclusion_ranges:
            if dhcp_range['start_ip'] < start_ip + exclusion_range[0]:
                dhcp_range['end_ip'] = start_ip + exclusion_range[0] - 1
                dhcp_range['properties']['end'] = str(ipaddress.ip_address(dhcp_range['end_ip']))
                ranges.append(dhcp_range)
            if  start_ip + exclusion_range[0] + exclusion_range[1] + 1 < end_ip:
                rest_dhcp_range['start_ip'] = \
                    start_ip + exclusion_range[0] + exclusion_range[1] + 1
                rest_dhcp_range['properties']['start'] = \
                    str(ipaddress.ip_address(rest_dhcp_range['start_ip']))
                dhcp_range = copy.deepcopy(rest_dhcp_range)
            else:
                rest_dhcp_range = None
        if rest_dhcp_range is not None:
            ranges.append(rest_dhcp_range)
    else:
        ranges.append(dhcp_range)
    return ranges

def calc_network_usage(api, connector, network_id):
    usage = 0
    dhcp_count = 0
    leased_count = 0
    
    if network_id != 0:
        dhcp_ranges = []
        dhcp_range_criteria = {
            'selector': 'get_entitytree',
            'startEntityId': network_id,
            'types': ObjectType.DHCP4_RANGE,
        }
        dhcp_range_index = 0
        while True:
            entities = list(api.export_entities(dhcp_range_criteria, dhcp_range_index, MAX_COUNT))
            for entity in entities:
                for dhcp_range in normalize_range(connector, entity):
                    dhcp_count += dhcp_range['end_ip'] - dhcp_range['start_ip'] + 1
                    dhcp_ranges.append(dhcp_range)
            entity_count = len(entities)
            if entity_count < MAX_COUNT:
                break
            dhcp_range_index += entity_count
        dhcp_ranges.sort(key = lambda node: node['start_ip'])
        
        ip_address_criteria = {
            'selector': 'get_entitytree',
            'startEntityId': network_id,
            'types': ObjectType.IP4_ADDRESS,
        }
        ip_address_index = 0
        while True:
            entities = list(api.export_entities(ip_address_criteria, ip_address_index, MAX_COUNT))
            for ip_address in entities:
                props = ip_address['properties']
                if is_inside_dhcp_range(dhcp_ranges, props['address']):
                    if props['state'] != IPAddressState.DHCP_FREE:
                        leased_count += 1
                elif  props['state'] == IPAddressState.DHCP_RESERVED:
                    dhcp_count += 1
                    leased_count += 1
                    
            entity_count = len(entities)
            if entity_count < MAX_COUNT:
                break
            ip_address_index += entity_count
            
        if 0 < dhcp_count:
            usage = leased_count * 100 / dhcp_count
    return dhcp_count, leased_count, usage

def get_network_id(api, config_id, cidr):
    network_id = 0
    network_criteria = {
        'selector': 'get_entitytree',
        'startEntityId': config_id,
        'types': ObjectType.IP4_BLOCK + ',' + ObjectType.IP4_NETWORK,
    }
    network_index = 0
    while True:
        entities = list(api.export_entities(network_criteria, network_index, MAX_COUNT))
        for network in entities:
            if get_range(network) == cidr:
                network_id = network['id']
                break
        if network_id != 0:
            break
            
        entity_count = len(entities)
        if entity_count < MAX_COUNT:
            break
        network_index += entity_count
    return network_id
    
def get_network_suggestions(api, config_id, range):
    suggestions = []
    
    network_criteria = {
        'selector': 'get_entitytree',
        'startEntityId': config_id,
        'types': ObjectType.IP4_BLOCK + ',' + ObjectType.IP4_NETWORK,
    }
    network_index = 0
    while True:
        entities = list(api.export_entities(network_criteria, network_index, MAX_COUNT))
        for network in entities:
            range_prop = get_range(network)
            if range_prop.startswith(range):
                suggestions.append(range_prop)
        entity_count = len(entities)
        if entity_count < MAX_COUNT:
            break
        network_index += entity_count
    return suggestions
