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
# Date: 2022-06-09
# Gateway Version: 21.11.2
# Description: Bulk Register DHCP Range

import ipaddress
import math

from bluecat_libraries.address_manager.api import Client
from bluecat_libraries.http_client.exceptions import ErrorResponse
from bluecat_libraries.address_manager.constants import (
    ObjectType,
    DHCPServiceOption,
    DHCPServiceOptionConstant
)

def get_range(entity):
    range = ''
    props = entity['properties']
    if 'CIDR' in props.keys():
        range = props['CIDR']
    else:
        range = props['start'] + '-' + props['end']
    return range
    
def normalize_range(range):
    if '-' not in range:
        return range
    else:
        start_end = range.split('-')
        start_ip = ipaddress.ip_address(start_end[0])
        end_ip = ipaddress.ip_address(start_end[1])
        size = int(end_ip) - int(start_ip) + 1
        range = start_end[0] + '/' + str(32 - int(math.log2(size)))
        network = ipaddress.ip_network(range) # for validation
    return range
    
def get_start_end_ips(range):
    start_ip = None
    end_ip = None
    if '-' in range:
        start_end = range.split('-')
        start_ip = ipaddress.ip_address(start_end[0])
        end_ip = ipaddress.ip_address(start_end
        [1])
    else:
        network = ipaddress.ip_network(range)
        start_ip = network.network_address
        end_ip = network.broadcast_address
    return start_ip, end_ip
    
def find_block(client, parent_id, block_range):
    block = None
    if '-' not in block_range:
        block = client.get_entity_by_cidr(parent_id, block_range, ObjectType.IP4_BLOCK)
    else:
        start_ip, end_ip = get_start_end_ips(block_range)
        for entity in client.get_entities(parent_id, ObjectType.IP4_BLOCK):
            st_ip, ed_ip = get_start_end_ips(get_range(entity))
            if (st_ip == start_ip) and (end_ip == ed_ip):
                block = entity
                break
    return block
        
def find_or_create_block(client, parent_id, block_range):
    block_id = 0
    try:
        block = find_block(client, parent_id, block_range)
        if block is not None:
            block_id = block['id']
        else:
            start_ip, end_ip = get_start_end_ips(block_range)
            for entity in client.get_entities(parent_id, ObjectType.IP4_BLOCK):
                st_ip, ed_ip = get_start_end_ips(get_range(entity))
                if (st_ip <= start_ip) and (end_ip <= ed_ip):
                    block_id = find_or_create_block(client, entity['id'], block_range)
                    break
            if block_id == 0:
                if '-' not in block_range:
                    block_id = client.add_ip4_block_by_cidr(parent_id, block_range)
                else:
                    block_id = client.add_ip4_block_by_range(parent_id, str(start_ip), str(end_ip))
                    
    except ErrorResponse as e:
        print(e.message)
        block_id = 0
    return block_id

def find_allow_mac_pool(client, parent_id, mac_pool_id):
    option_id = 0
    try:
        for option in client.get_deployment_options(parent_id, 0, ['DHCPServiceOption']):
            props = option['properties']
            if props['inherited'] == 'true':
                continue
                
            if option['type'] == 'DHCPService' and option['name'] == 'allow-mac-pool':
                if props['macPool'] == str(mac_pool_id):
                    option_id = option['id']
                    break
                    
    except ErrorResponse as e:
        print(e.message)
        option_id = 0
    return option_id
    
def find_or_add_allow_mac_pool(client, configuration_id, parent_id, pool):
    option_id = 0
    try:
        mac_pool = client.get_entity_by_name(configuration_id, pool, ObjectType.MAC_POOL)
        if mac_pool is not None:
            option_id = find_allow_mac_pool(client, parent_id, mac_pool['id'])
            if option_id == 0:
                option_id = client.add_dhcp_service_deployment_option(
                    parent_id,
                    DHCPServiceOption.ALLOW_MAC_POOL,
                    [],
                    properties={'macPool': mac_pool['id']}
                )
    except ErrorResponse as e:
        print(e.message)
        option_id = 0
    return option_id
    
def find_or_create_network(client, parent_id, network_range, gateway):
    network_id = 0
    try:
        network_cidr = normalize_range(network_range)
        network = client.get_entity_by_cidr(parent_id, network_cidr, ObjectType.IP4_NETWORK)
        if network is not None:
            network_id = network['id']
        else:
            props = None
            if gateway != '':
                props = {'gateway': gateway}
            network_id = client.add_ip4_network(parent_id, network_cidr, props)
            
    except ErrorResponse as e:
        print(e.message)
        network_id = 0
    except ValueError as ve:
        network_id = 0
    return network_id

def find_or_create_tag(client, parent_id, tag_name):
    tag_id = 0
    try:
        tag = client.get_entity_by_name(parent_id, tag_name, ObjectType.TAG)
        if tag is not None:
            tag_id = tag['id']
        else:
            tag_id = client.add_tag(parent_id, tag_name)
            
    except ErrorResponse as e:
        print(e.message)
        tag_id = 0
    return tag_id

def add_dhcp_range(client, parent_id, dhcp_range):
    start_end = dhcp_range.split('-')
    dhcp_range_id = 0
    try:
        dhcp_range_id = client.add_dhcp4_range(parent_id, start_end[0], start_end[1])
    except ErrorResponse as e:
        print(e.message)
        dhcp_range_id = 0
    return dhcp_range_id


def add_dhcp_ranges(client, configuration_id, tag_group_id, dhcp_ranges):
    for dhcp_range in dhcp_ranges:
        block_id = find_or_create_block(client, configuration_id, dhcp_range['block'])
        if block_id == 0:
            print(f"Error: Could not create '{dhcp_range['block']}' Block.")
            continue
            
        if dhcp_range['pools'] != '':
            for pool in dhcp_range['pools'].split('|'):
                option_id = find_or_add_allow_mac_pool(client, configuration_id, block_id, pool)
                if option_id == 0:
                    print(f"Error: Could not add Allow MAC Pool '{pool}' option to '{dhcp_range['block']}' Block.")
                    continue
                    
        if dhcp_range['network'] != '':
            network_id = find_or_create_network(client, block_id, dhcp_range['network'], dhcp_range['gateway'])
            if network_id == 0:
                print(f"Error: Could not create '{dhcp_range['network']}' Network.")
                continue
            
            if dhcp_range['tag'] != '':
                tag_id = find_or_create_tag(client, tag_group_id, dhcp_range['tag'])
                if tag_id == 0:
                    print(f"Error: Could not create '{dhcp_range['tag']}' tag.")
                    continue
                
                client.share_network(network_id, tag_id)
                
            if dhcp_range['range'] != '':
                dhcp_range_id = add_dhcp_range(client, network_id, dhcp_range['range'])
                if dhcp_range_id == 0:
                    print(f"Error: Could not add '{dhcp_range['range']}' DHCP Range at '{dhcp_range['network']}'.")
                    continue
                    
                    

