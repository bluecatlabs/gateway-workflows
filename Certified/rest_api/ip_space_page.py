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

from flask import jsonify
from flask_restplus import Resource

import bluecat.server_endpoints as se
from bluecat import util
from bluecat.entity import Entity
from main_app import api
from .configuration_page import config_defaults
from .library.models.entity_models import entity_return_model
from .library.models.ip4_address_models import ip4_address_post_model, ip4_address_patch_model, \
    network_patch_model, network_post_model, network_add_model, block_post_model, next_ip4_address_post_model
from .library.parsers.deployment_parsers import deployment_option_post_parser, deployment_role_post_parser
from .library.parsers.ip4_address_parsers import block_post_parser, network_patch_parser, \
    network_post_parser, network_add_parser, ip4_address_post_parser, ip4_address_patch_parser
from .option_and_role_utils import *

ip4_address_root_default_ns = api.namespace('ipv4_addresses', description='IPv4 Address operations')
ip4_address_root_ns = api.namespace(
    'ipv4_addresses',
    path='/configurations/<string:configuration>/',
    description='IPv4 Address operations',
)

ip4_address_default_ns = api.namespace('ipv4_addresses', description='IPv4 Address operations')
ip4_address_ns = api.namespace(
    'ipv4_addresses',
    path='/configurations/<string:configuration>/',
    description='IPv4 Address operations',
)

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

ip4_network_group_ns = api.namespace('ipv4_networks', path='/tag_group/<string:tag_group>/',
                                     description='IPv4 Network operations')
ip4_network_config_group_ns = api.namespace(
    'ipv4_networks',
    path='/configurations/<string:configuration>/tag_group/<string:tag_group>/',
    description='IPv4 Network operations',
)


@ip4_address_ns.route('/ipv4_networks/<string:network>/get_next_ip/')
@ip4_address_default_ns.route('/ipv4_networks/<string:network>/get_next_ip/', defaults=config_defaults)
@ip4_address_ns.response(404, 'IPv4 address not found')
class IPv4NextIP4Address(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @ip4_address_ns.response(201, 'Next IP successfully created.', model=entity_return_model)
    @ip4_address_ns.expect(next_ip4_address_post_model, validate=True)
    def post(self, configuration, network):
        """
        Create the next available IP4 Address

        Network can be of the format of network address:
        1. 10.1.0.0

        """
        data = ip4_address_post_parser.parse_args()
        mac = data.get('mac_address', '')
        hostinfo = data.get('hostinfo', '')
        action = data.get('action', '')
        properties = data.get('properties', '')

        configuration = g.user.get_api().get_configuration(configuration)
        network = configuration.get_ip_range_by_ip(Entity.IP4Network, network)

        ip = network.assign_next_available_ip4_address(mac, hostinfo, action, properties)
        result = ip.to_json()

        return result, 201

    @util.rest_workflow_permission_required('rest_page')
    @ip4_address_ns.response(200, 'Next IP found.', model=entity_return_model)
    def get(self, configuration, network):
        """
        Get the next available IP address

        Network can be of the format of network address:
        1. 10.1.0.0
        """
        configuration = g.user.get_api().get_configuration(configuration)
        network = configuration.get_ip_ranged_by_ip("IP4Network", network)
        ip = network.get_next_available_ip4_address()

        return ip, 200


@ip4_address_ns.route('/ipv4_address/<string:ipv4_address>/')
@ip4_address_default_ns.route('/ipv4_address/<string:ipv4_address>/', defaults=config_defaults)
@ip4_address_ns.response(200, 'IP4 Address found.', model=entity_return_model)
class IPv4Address(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, ipv4_address):
        """
        Get an IP4 Address

        """
        configuration = g.user.get_api().get_configuration(configuration)

        try:
            result = se.get_address_data(configuration.get_id(), ipv4_address)
            if result['status'] == 'FAIL':
                raise Exception
            name = ""
            ip_id = 0
            properties = ""
            if result['data']['state'] != 'UNALLOCATED':
                ip = configuration.get_ip4_address(ipv4_address)
                ip_id = ip.get_id()
                name = ip.get_name()
                properties = ""
                for prop, value in ip.get_properties().items():
                    properties += prop + "=" + value + "|"

            response = {
                'id': ip_id,
                'name': name,
                'properties': properties,
                'type': 'IP4Address'
            }
            return response
        except Exception:
            return 'IPv4 address not found', 404

    @util.rest_workflow_permission_required('rest_page')
    @ip4_network_ns.expect(ip4_address_patch_model, validate=True)
    def patch(self, configuration, ipv4_address):
        """
        Update IPv4 Address.
        """
        data = ip4_address_patch_parser.parse_args()
        try:
            configuration = g.user.get_api().get_configuration(configuration)
            address = configuration.get_ip4_address(ipv4_address)
        except Exception as e:
            return util.safe_str(e), 404
        try:
            if data['mac_address'] is not None:
                address.set_property('macAddress', data['mac_address'])
            if data['action'] is not None:
                address.change_state_ip4_address(data['action'], data['mac_address'])
            if data['properties'] is not None:
                properties = data.get('properties')
                address.set_properties(util.properties_to_map(properties))
            address.update()
            result = address.to_json()
            return jsonify(result)
        except Exception as e:
            return util.safe_str(e), 409

    @util.rest_workflow_permission_required('rest_page')
    @ip4_address_ns.expect(ip4_address_post_model, validate=True)
    def post(self, configuration, ipv4_address):
        """
        Assign an IP Address that is not the next available one

        Network can be of the format of network address:
        1. 10.1.0.0

        """
        data = ip4_address_post_parser.parse_args()
        mac = data.get('mac_address', '')
        hostinfo = data.get('hostinfo', '')
        action = data.get('action')
        properties = data.get('properties', '')

        configuration = g.user.get_api().get_configuration(configuration)
        network = configuration.get_ip_ranged_by_ip("IP4Network", ipv4_address)

        ip = network.assign_ip4_address(ipv4_address, mac, hostinfo, action, properties)
        return ip.to_json(), 201


@ip4_block_ns.route('/<path:block>/get_next_network/')
@ip4_block_default_ns.route('/<path:block>/get_next_network/', defaults=config_defaults)
@ip4_block_ns.response(404, 'IPv4 network not found')
class IPv4NextNetworkCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @ip4_block_ns.response(201, 'Next network successfully created.', model=entity_return_model)
    @ip4_block_ns.expect(network_post_model, validate=True)
    def post(self, configuration, block):
        """
        Create the next available IP4 Network

        Blocks can be of the format:
        1. 10.1.0.0/16
        2. 10.0.0.0/8/ipv4_blocks/10.1.0.0/24

        """
        data = network_post_parser.parse_args()
        name = data.get('name', '')
        size = data.get('size', '')
        properties = data.get('properties', '')
        destination_obj = g.user.get_api().get_configuration(configuration)
        block_hierarchy = []
        if block:
            block_hierarchy = block.split('ipv4_blocks')

        for block in block_hierarchy:
            block_cidr = block.strip('/')
            destination_obj = destination_obj.get_entity_by_cidr(block_cidr, Entity.IP4Block)
        network = destination_obj.get_next_available_ip_range(size, Entity.IP4Network, properties)
        network.set_name(name)
        network.update()
        result = network.to_json()

        return result, 201


@ip4_block_ns.route('/<path:block>/create_network/')
@ip4_block_default_ns.route('/<path:block>/create_network/', defaults=config_defaults)
@ip4_block_ns.response(500, 'Error creating network')
class IPv4CustomNetwork(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @ip4_block_ns.response(201, 'Network successfully created.', model=entity_return_model)
    @ip4_block_ns.expect(network_add_model, validate=True)
    def post(self, configuration, block):
        """
        Create an IP4 Network

        Blocks can be of the format:
        1. 10.1.0.0/16
        2. 10.0.0.0/8/ipv4_blocks/10.1.0.0/24

        Network can be of the format:
        10.1.1.0/24
        """
        data = network_add_parser.parse_args()
        range = g.user.get_api().get_configuration(configuration)
        block_hierarchy = []
        if block:
            block_hierarchy = block.split('ipv4_blocks')

        for block in block_hierarchy:
            block_cidr = block.strip('/')
            range = range.get_entity_by_cidr(block_cidr, range.IP4Block)
        network = range.add_ip4_network(cidr=data.get('cidr'), properties=data.get('properties', ''))

        return network.to_json(), 201


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
        destination_obj = g.user.get_api().get_configuration(configuration)
        block_hierarchy = []
        if block:
            block_hierarchy = block.split('ipv4_blocks')

        for block in block_hierarchy:
            block_cidr = block.strip('/')
            destination_obj = destination_obj.get_entity_by_cidr(block_cidr, Entity.IP4Block)
        blocks = destination_obj.get_ip4_blocks()

        result = [block_entity.to_json() for block_entity in blocks]
        return jsonify(result)

    @util.rest_workflow_permission_required('rest_page')
    @ip4_block_ns.response(201, 'Block successfully created.', model=entity_return_model)
    @ip4_block_ns.expect(block_post_model, validate=True)
    def post(self, configuration, block=None):
        """
        Create IP4 Block
        """
        data = block_post_parser.parse_args()
        name = data.get('name', '')
        address = data.get('address', '')
        cidr = data.get('cidr_notation', '')
        properties = data.get('properties', '')
        config = g.user.get_api().get_configuration(configuration)
        try:
            container = config.get_ip_range_by_ip(Entity.IP4Block, address)
        except:
            container = config
        block = container.add_ip4_block_by_cidr("%s/%s" % (address, cidr), properties)
        block.set_name(name)
        block.update()
        result = block.to_json()
        return result, 201


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
        destination_obj = g.user.get_api().get_configuration(configuration)
        block_hierarchy = block.split('ipv4_blocks')

        for block in block_hierarchy:
            block_cidr = block.strip('/')
            destination_obj = destination_obj.get_entity_by_cidr(block_cidr, Entity.IP4Block)

        result = destination_obj.to_json()
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
        destination_obj = g.user.get_api().get_configuration(configuration)
        block_hierarchy = block.split('ipv4_blocks')
        for block in block_hierarchy:
            block_cidr = block.strip('/')

            destination_obj = destination_obj.get_entity_by_cidr(block_cidr, Entity.IP4Block)
        networks = destination_obj.get_children_of_type(Entity.IP4Network)

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
        network_range = configuration.get_ip_range_by_ip(Entity.IP4Network, network_ip)

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
        network_range = configuration.get_ip_range_by_ip(Entity.IP4Network, network_ip)

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
        network_range = configuration.get_ip_range_by_ip(Entity.IP4Network, network_ip)

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


@ip4_network_config_group_ns.route('/tags/<string:tag>/ipv4_networks/')
@ip4_network_group_ns.route('/tags/<string:tag>/ipv4_networks/', defaults=config_defaults)
class LinkedIPv4NetWork(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, tag_group, tag):
        """
        Get IPv4 Network linked with tags.
        """
        try:
            results = []
            tags = g.user.get_api().get_by_object_types(tag, 'Tag')
            for val in tags:
                if val.get_parent().name == tag_group:
                    networks = val.get_linked_entities(Entity.IP4Network)
                    if configuration != '':
                        for network in networks:
                            config_of_network = network.get_parent_configuration()
                            if config_of_network.get_name() == configuration:
                                results.append(network.to_json())
                    else:
                        for network in networks:
                            results.append(network.to_json())
            if len(results) == 0:
                return 'IPv4 Network in tag not found', 404
            return jsonify(results)
        except Exception as e:
            return str(e), 500


@ip4_network_ns.route('/<path:network>/option_name/<string:option_name>/server/<path:server_id>/deployment_options/')
@ip4_network_default_ns.route(
    '/<path:network>/option_name/<string:option_name>/server/<path:server_id>/deployment_options/',
    defaults=config_defaults
)
@ip4_block_ns.route('/<path:block>/option_name/<string:option_name>/server/<path:server_id>/deployment_options/')
@ip4_block_default_ns.route(
    '/<path:block>/option_name/<string:option_name>/server/<path:server_id>/deployment_options/',
    defaults=config_defaults
)
class DeploymentOptionCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, option_name, server_id, block=None, network=None):
        """
        Find a deployment option set on the Block or Network, by name and assigned server ID

        Server ID can be:

        1. 0 if the option is set to All Servers
        2. The entity ID of the assigned server or server group
        3. -1 if you are not sure which of the above to use
        """
        configuration = g.user.get_api().get_configuration(configuration)

        if network:
            network_ip = network.split('/')[0]
            network_range = configuration.get_ip_ranged_by_ip(configuration.IP4Network, network_ip)
            return get_option(network_range, option_name, int(server_id))
        elif block:
            range = configuration
            block_hierarchy = block.split('ipv4_blocks')
            for block in block_hierarchy:
                block_cidr = block.strip('/')
                range = range.get_entity_by_cidr(block_cidr)
            return get_option(range, option_name, int(server_id))

    @util.rest_workflow_permission_required('rest_page')
    def delete(self, configuration, option_name, server_id, block=None, network=None):
        """
        Delete a deployment option set on the block or network, by name and assigned server ID

        Server ID can be:

        1. 0 if the option is set to All Servers
        2. The entity ID of the assigned server or server group
        """
        configuration = g.user.get_api().get_configuration(configuration)
        if int(server_id) < 0:
            return 'Server ID must be 0 or higher for delete function', 400

        if network:
            network_ip = network.split('/')[0]
            network_range = configuration.get_ip_ranged_by_ip(configuration.IP4Network, network_ip)
            return del_option(network_range, option_name, int(server_id))
        elif block:
            range = configuration
            block_hierarchy = block.split('ipv4_blocks')
            for block in block_hierarchy:
                block_cidr = block.strip('/')
                range = range.get_entity_by_cidr(block_cidr)
            return del_option(range, option_name, int(server_id))


@ip4_network_ns.route('/<path:network>/deployment_options/')
@ip4_network_default_ns.route('/<path:network>/deployment_options/', defaults=config_defaults)
@ip4_block_ns.route('/<path:block>/deployment_options/')
@ip4_block_default_ns.route('/<path:block>/deployment_options/', defaults=config_defaults)
class DeploymentOption(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @ip4_network_ns.expect(deployment_option_post_model, validate=True)
    @ip4_network_default_ns.expect(deployment_option_post_model, validate=True)
    @ip4_block_ns.expect(deployment_option_post_model, validate=True)
    @ip4_block_default_ns.expect(deployment_option_post_model, validate=True)
    def post(self, configuration, block=None, network=None):
        """
        Add a DNS or DHCP Deployment Option to a block or network
        """
        configuration = g.user.get_api().get_configuration(configuration)
        data = deployment_option_post_parser.parse_args()

        if network:
            network_ip = network.split('/')[0]
            network_range = configuration.get_ip_ranged_by_ip(configuration.IP4Network, network_ip)
            return add_option(network_range, data)
        elif block:
            range = configuration
            block_hierarchy = block.split('ipv4_blocks')
            for block in block_hierarchy:
                block_cidr = block.strip('/')
                range = range.get_entity_by_cidr(block_cidr)
            return add_option(range, data)


@ip4_network_ns.route('/<path:network>/role_type/<string:role_type>/server/<path:server_fqdn>/deployment_roles/')
@ip4_network_default_ns.route(
    '/<path:network>/role_type/<string:role_type>/server/<path:server_fqdn>/deployment_roles/',
    defaults=config_defaults
)
@ip4_block_ns.route('/<path:block>/role_type/<string:role_type>/server/<path:server_fqdn>/deployment_roles/')
@ip4_block_default_ns.route(
    '/<path:block>/role_type/<string:role_type>/server/<path:server_fqdn>/deployment_roles/',
    defaults=config_defaults
)
class DeploymentRoleCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, role_type, server_fqdn, block=None, network=None):
        """
        Find a Deployment Role set on the Block or Network, by type and assigned server interface
        """
        configuration = g.user.get_api().get_configuration(configuration)

        if network:
            network_ip = network.split('/')[0]
            network_range = configuration.get_ip_ranged_by_ip(configuration.IP4Network, network_ip)
            return get_role(network_range, role_type, server_fqdn)
        elif block:
            range = configuration
            block_hierarchy = block.split('ipv4_blocks')
            for block in block_hierarchy:
                block_cidr = block.strip('/')
                range = range.get_entity_by_cidr(block_cidr)
            return get_role(range, role_type, server_fqdn)

    @util.rest_workflow_permission_required('rest_page')
    def delete(self, configuration, role_type, server_fqdn, block=None, network=None):
        """
        Delete a Deployment Role set on the block or network, by name and assigned server interface
        """
        configuration = g.user.get_api().get_configuration(configuration)

        if network:
            network_ip = network.split('/')[0]
            network_range = configuration.get_ip_ranged_by_ip(configuration.IP4Network, network_ip)
            return del_role(network_range, role_type, server_fqdn)
        elif block:
            range = configuration
            block_hierarchy = block.split('ipv4_blocks')
            for block in block_hierarchy:
                block_cidr = block.strip('/')
                range = range.get_entity_by_cidr(block_cidr)
            return del_role(range, role_type, server_fqdn)


@ip4_network_ns.route('/<path:network>/deployment_roles/')
@ip4_network_default_ns.route('/<path:network>/deployment_roles/', defaults=config_defaults)
@ip4_block_ns.route('/<path:block>/deployment_roles/')
@ip4_block_default_ns.route('/<path:block>/deployment_roles/', defaults=config_defaults)
class DeploymentRole(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @ip4_network_ns.expect(deployment_role_post_model, validate=True)
    @ip4_network_default_ns.expect(deployment_role_post_model, validate=True)
    @ip4_block_ns.expect(deployment_role_post_model, validate=True)
    @ip4_block_default_ns.expect(deployment_role_post_model, validate=True)
    def post(self, configuration, block=None, network=None):
        """
        Add a DNS or DHCP Deployment Role to a block or network
        """
        configuration = g.user.get_api().get_configuration(configuration)
        data = deployment_role_post_parser.parse_args()

        if network:
            network_ip = network.split('/')[0]
            network_range = configuration.get_ip_ranged_by_ip(configuration.IP4Network, network_ip)
            return add_role(network_range, data)
        elif block:
            range = configuration
            block_hierarchy = block.split('ipv4_blocks')
            for block in block_hierarchy:
                block_cidr = block.strip('/')
                range = range.get_entity_by_cidr(block_cidr)
            return add_role(range, data)
