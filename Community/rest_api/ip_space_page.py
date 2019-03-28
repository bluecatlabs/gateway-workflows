# Copyright 2018 BlueCat Networks (USA) Inc. and its affiliates
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
# limitations under the License.
#
# By: Xiao Dong (xdong@bluecatnetworks.com)
#     Anshul Sharma (asharma@bluecatnetworks.com)
# Date: 06-09-2018
# Gateway Version: 18.9.1
# Description: This workflow will provide access to a REST based API for Gateway.
#              Once imported, documentation for the various end points available can
#              be viewed by navigating to /api/v1/.

from flask import g, jsonify
from flask_restplus import fields, reqparse, Resource

from bluecat import util
from .configuration_page import config_defaults
from main_app import api


ip4_block_root_default_ns = api.namespace('ipv4_blocks', description='IPv4 Block operations')
ip4_block_root_ns = api.namespace(
    'ipv4_blocks',
    path='/configurations/<string:configuration>/ipv4_blocks/',
    description='IPv4 Block operations',
)

ip4_block_default_ns = api.namespace('ipv4_blocks', description='IPv4 Block operations')
ip4_block_ns = api.namespace(
    'ipv4_blocks',
    path='/configurations/<string:configuration>/ipv4_blocks/',
    description='IPv4 Block operations',
)

ip4_network_default_ns = api.namespace('ipv4_networks', description='IPv4 Network operations')
ip4_network_ns = api.namespace(
    'ipv4_networks',
    path='/configurations/<string:configuration>/ipv4_networks/',
    description='IPv4 Network operations',
)

ip4_network_block_ns = api.namespace('ipv4_networks', path='/ipv4_blocks/', description='IPv4 Network operations')
ip4_network_config_block_ns = api.namespace(
    'ipv4_networks',
    path='/configurations/<string:configuration>/ipv4_blocks/',
    description='IPv4 Network operations',
)

network_patch_model = api.model(
    'ipv4_networks_patch',
    {
        'name':  fields.String(description='The name associated with the IP4 Network.'),
        'properties':  fields.String(description='The properties of the host record', default='attribute=value|'),
    },
)

network_patch_parser = reqparse.RequestParser()
network_patch_parser.add_argument('name', location="json", help='The name of the network')
network_patch_parser.add_argument('properties', location="json", help='The properties of the record')


@ip4_block_root_ns.route('/')
@ip4_block_ns.route('/<path:block>/ipv4_blocks/')
@ip4_block_root_default_ns.route('/', defaults=config_defaults)
@ip4_block_default_ns.route('/<path:block>/ipv4_blocks/', defaults=config_defaults)
@ip4_block_ns.response(404, 'IPv4 Blocks not found')
class IPv4BlockCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, block=None):
        """
        Get all direct child IPv4 Blocks belonging to default or provided Configuration and Block hierarchy.
        Blocks can be recursively retrieved by specifying extra ipv4_block parameters.
        Blocks can be of the format:

        1. 10.1.0.0/16
        2. 10.1.0.0/16/ipv4_blocks/10.1.1.0/24/ipv4_blocks/
        """
        range = g.user.get_api().get_configuration(configuration)
        block_hierarchy = []
        if block:
            block_hierarchy = block.split('ipv4_blocks')

        for block in block_hierarchy:
            block_cidr = block.strip('/')
            range = range.get_entity_by_cidr(block_cidr, range.IP4Block)
        blocks = range.get_ip4_blocks()

        result = [block_entity.to_json() for block_entity in blocks]
        return jsonify(result)


@ip4_block_ns.route('/<path:block>/')
@ip4_block_default_ns.route('/<path:block>/', defaults=config_defaults)
@ip4_block_ns.param('block', 'Recursive')
@ip4_block_ns.response(404, 'No matching IPv4 Block(s) found')
class IPv4Block(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, block):
        """
        Get IPv4 Block belonging to default or provided Configuration and Block hierarchy.
        Blocks can be recursively retrieved by specifying extra ipv4_block parameters.
        Blocks can be of the format:

        1. 10.1.0.0/16
        2. 10.1.0.0/16/ipv4_blocks/10.1.1.0/24
        """
        range = g.user.get_api().get_configuration(configuration)
        block_hierarchy = block.split('ipv4_blocks')

        for block in block_hierarchy:
            block_cidr = block.strip('/')
            range = range.get_entity_by_cidr(block_cidr, range.IP4Block)

        result = range.to_json()
        return jsonify(result)


@ip4_network_config_block_ns.route('/<path:block>/ipv4_networks/')
@ip4_network_block_ns.route('/<path:block>/ipv4_networks/', defaults=config_defaults)
@ip4_network_config_block_ns.param('block', 'Recursive')
@ip4_block_ns.response(404, 'No matching IPv4 Network(s) found')
class IPv4NetworkCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, block):
        """
        Get all IPv4 Networks belonging to default or provided Configuration and Block hierarchy.
        Path can be of the format:

        1. ipv4_blocks/10.1.0.0/16/ipv4_blocks/10.1.1.0/24/ipv4_networks/
        """
        range = g.user.get_api().get_configuration(configuration)
        block_hierarchy = block.split('ipv4_blocks')
        for block in block_hierarchy:
            block_cidr = block.strip('/')

            range = range.get_entity_by_cidr(block_cidr, range.IP4Block)
        networks = range.get_children_of_type(range.IP4Network)

        result = [network.to_json() for network in networks]
        return jsonify(result)


@ip4_network_ns.route('/<path:network>/')
@ip4_network_default_ns.route('/<path:network>/', defaults=config_defaults)
@ip4_network_ns.response(404, 'No matching IPv4 Network(s) found')
class IPv4Network(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, network):
        """
        Get IPv4 Network belonging to default or provided Configuration.
        Network can be of the format:

        1. 10.1.1.0
        2. 10.1.1.0/24
        """
        configuration = g.user.get_api().get_configuration(configuration)
        network_ip = network.split('/')[0]
        network_range = configuration.get_ip_range_by_ip(configuration.IP4Network, network_ip)

        if '/' in network and network_range.get_property('CIDR') != network:
            return 'No matching IPv4 Network(s) found', 404
        result = {'id': network_range.get_id(), 'name': network_range.get_name()}
        return jsonify(result)

    @util.rest_workflow_permission_required('rest_page')
    def delete(self, configuration, network):
        """
        Delete IPv4 Network belonging to default or provided Configuration.
        Network can be of the format:

        1. 10.1.1.0
        2. 10.1.1.0/24
        """
        configuration = g.user.get_api().get_configuration(configuration)
        network_ip = network.split('/')[0]
        network_range = configuration.get_ip_range_by_ip(configuration.IP4Network, network_ip)

        if '/' in network and network_range.get_property('CIDR') != network:
            return 'No matching IPv4 Network(s) found', 404
        network_range.delete()
        return '', 204

    @util.rest_workflow_permission_required('rest_page')
    @ip4_network_ns.expect(network_patch_model, validate=True)
    def patch(self, configuration, network):
        """
        Update IPv4 Network belonging to default or provided Configuration.
        Network can be of the format:

        1. 10.1.1.0
        2. 10.1.1.0/24
        """
        data = network_patch_parser.parse_args()
        configuration = g.user.get_api().get_configuration(configuration)
        network_ip = network.split('/')[0]
        network_range = configuration.get_ip_range_by_ip(configuration.IP4Network, network_ip)

        if network_range is None:
            return 'No matching IPv4 Network(s) found', 404
        if '/' in network and network_range.get_property('CIDR') != network:
            return 'No matching IPv4 Network(s) found', 404

        if data['properties'] is not None:
            properties = data.get('properties')
            network_range.set_properties(util.properties_to_map(properties))
        if data['name'] is not None:
            network_range.set_name(data['name'])
        network_range.update()
        result = network_range.to_json()
        return jsonify(result)

