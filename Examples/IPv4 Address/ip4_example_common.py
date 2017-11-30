# Copyright 2017 BlueCat Networks (USA) Inc. and its affiliates
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

import struct
import ipaddress
from socket import inet_aton

from flask import url_for, redirect, render_template, flash, g, request, jsonify
from bluecat.api_exception import APIException, PortalException, BAMException
from bluecat import util


def get_networks(configuration_id, hint):
    result = []

    # Retrieve the configuration object
    configuration = g.user.get_api().get_entity_by_id(configuration_id)

    # If no user input (null) then set hint to empty to pre-populate the dropdown, otherwise search with user input
    if not hint:
        properties = ''
    else:
        properties = hint

    # Retrieve the network objects
    try:
        ip4_networks = configuration.get_ip4_networks_by_hint(properties.split('/')[0])  # remove CIDR
    except APIException:
        ip4_networks = []

    # If valid networks are retrieved then extract the absolute IP/CIDR and append to result
    for ip4_network in ip4_networks:
        result.append(ip4_network.get_property('CIDR'))

    return jsonify(result)


def get_addresses(configuration_id, network):
    result = []
    try:
        # Retrieve the configuration object
        configuration = g.user.get_api().get_entity_by_id(configuration_id)

        # Network is sent with an arbitrary character to replace the / that will interfere with flask
        network = network.replace('A', '/')

        # Check if a valid network is entered, else raise exception
        ipaddress.ip_network(network)

        # Create a list to extract the CIDR
        network_list = network.split('/')

        # Retrieve IP network from network_list
        ip4_network = configuration.get_ip4_networks_by_hint(util.safe_str(network_list[0]))

        # Retrieve IP4Address children of network to create list of taken addresses
        children_addresses = ip4_network[0].get_children_of_type('IP4Address')

        # Append all children addresses to results array
        for address in children_addresses:
            result.append(util.safe_str(address.get_property('address')))
            if len(result) >= 10:
                break

        # Sort IP List
        result = sorted(result, key=lambda ip: struct.unpack("!L", inet_aton(ip))[0])

        return jsonify(result)
    except Exception as e:
        if ('does not appear to be an IPv4 or IPv6 network' in util.safe_str(e)) or ('has host bits set' in util.safe_str(e)):
            g.user.logger.warning('%s' % e, msg_type=g.user.logger.EXCEPTION)
            return jsonify([])
        else:
            raise e


def address_unused(configuration_id, address):
    result = []
    configuration = g.user.get_api().get_entity_by_id(configuration_id)

    try:
        configuration.get_ip_range_by_ip(configuration.IP4Network, address)
    except PortalException:
        return jsonify(result)

    try:
        ip4_address = configuration.get_ip4_address(address)
    except PortalException:
        state = None
    else:
        state = ip4_address.get_property('state')

    if not state and not address.endswith('.0'):
        result.append(address)
    return jsonify(result)


def get_address_data(configuration_id, ip4_address):
    result = {
        'state': 'UNALLOCATED',
        'mac_address': '',
        'name': ''
    }

    # Retrieve the configuration object
    configuration = g.user.get_api().get_entity_by_id(configuration_id)

    # Retrieve the IP4 address object
    try:
        ip4_address = configuration.get_ip4_address(ip4_address)
    except (PortalException, BAMException) as e:
        g.user.logger.warning('%s' % e, msg_type=g.user.logger.EXCEPTION)
        return jsonify(result)

    # Retrieve the IP4 object name and mac address properties
    state = ip4_address.get_property('state')
    if not state:
        state = 'UNALLOCATED'

    result = {
        'state': state,
        'mac_address': ip4_address.get_property('macAddress'),
        'name':ip4_address.get_name()
    }
    return jsonify(result)
