# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: Xiao Dong, Anshul Sharma, Chris Storz (cstorz@bluecatnetworks.com) Date: 06-09-2018
# Gateway Version: 19.8.1
# Description: This workflow will provide access to a REST-based API for BlueCat Gateway.
#              Once imported and permissioned, documentation for the various available endpoints
#              can be viewed by navigating to /api/v1/.

from flask import jsonify
from flask_restplus import Resource

import bluecat.server_endpoints as se
import config.default_config as config
from bluecat import util
from main_app import api
from .configuration_page import config_doc, config_defaults
from .library.models.dns_models import zone_model, external_host_model, host_model, host_patch_model, \
    cname_model, cname_patch_model, view_model
from .library.models.entity_models import entity_return_model
from .library.parsers.deployment_parsers import deployment_option_post_parser, deployment_role_post_parser
from .library.parsers.dns_parsers import host_parser, host_patch_parser, cname_parser, \
    external_host_parser, cname_patch_parser
from .library.parsers.entity_parsers import entity_parser
from .option_and_role_utils import *

view_default_ns = api.namespace('views', path='/views/', description='View operations')
view_ns = api.namespace('views', path='/configurations/<string:configuration>/views/', description='View operations')

zone_default_root_ns = api.namespace('zones', description='Zone operations')
zone_root_ns = api.namespace(
    'zones',
    path='/configurations/<string:configuration>/views/<string:view>/zones/',
    description='Zone operations',
)

zone_default_ns = api.namespace('zones', description='Zone operations')
zone_ns = api.namespace(
    'zones',
    path='/configurations/<string:configuration>/views/<string:view>/zones/',
    description='Zone operations',
)

host_default_ns = api.namespace('host_records', description='Host Record operations')
host_ns = api.namespace(
    'host_records',
    path='/configurations/<string:configuration>/views/<string:view>/host_records/',
    description='Host Record operations',
)

external_host_default_ns = api.namespace('host_records', description='External Host Record operations')
external_host_ns = api.namespace(
    'host_records',
    path='/configurations/<string:configuration>/views/<string:view>/external_host_records/',
    description='External Host Record operations',
)

host_zone_default_ns = api.namespace(
    'host_records',
    path='/zones/<path:zone>/host_records',
    description='Host Record operations',
)
host_zone_ns = api.namespace(
    'host_records',
    path='/configurations/<string:configuration>/views/<string:view>/zones/<path:zone>/host_records/',
    description='Host Record operations',
)

cname_default_ns = api.namespace('cname_records', description='CName Record operations')
cname_ns = api.namespace(
    'cname_records',
    path='/configurations/<string:configuration>/views/<string:view>/cname_records/',
    description='CName Record operations',
)

cname_zone_default_ns = api.namespace(
    'cname_records',
    path='/zones/<path:zone>/cname_records',
    description='CName Record operations',
)
cname_zone_ns = api.namespace(
    'cname_records',
    path='/configurations/<string:configuration>/views/<string:view>/zones/<path:zone>/cname_records/',
    description='CName Record operations',
)

view_doc = dict(config_doc, view={'in': 'path', 'description': 'View name'})
zone_doc = dict(view_doc, zone={'in': 'path', 'description': 'Recursive Zone name and subzone name'})
absolute_name_doc = {'absolute_name': {'in': 'path', 'description': 'The FQDN of the record'}}
host_doc = dict(view_doc, **absolute_name_doc)

dns_defaults = {'configuration': config.default_configuration, 'view': config.default_view}


@view_ns.route('/<string:view>/')
@view_default_ns.route('/<string:view>/', defaults=config_defaults)
@view_ns.doc(params=view_doc)
@view_ns.response(200, 'View found.', model=entity_return_model)
class View(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, view):
        """ Get View belonging to default or provided Configuration. """
        configuration = g.user.get_api().get_configuration(configuration)
        view = configuration.get_view(view)
        result = view.to_json()
        return result

    @util.rest_workflow_permission_required('rest_page')
    def delete(self, configuration, view):
        """ Delete View belonging to default or provided Configuration. """
        configuration = g.user.get_api().get_configuration(configuration)
        view = configuration.get_view(view)
        view.delete()
        return '', 204


@view_ns.route('/')
@view_default_ns.route('/', defaults=config_defaults)
class ViewCollection(Resource):

    @view_ns.expect(view_model, validate=True)
    @view_ns.response(201, 'View Created', model=entity_return_model)
    @util.rest_workflow_permission_required('rest_page')
    def post(self, configuration):
        """Create a View belonging to the default or provided Configuration"""
        data = entity_parser.parse_args()
        properties = data.get('properties', '')
        configuration = g.user.get_api().get_configuration(configuration)
        view = configuration.add_view(data.get('name'), properties)
        return view.to_json(), 201


@zone_ns.route('/<path:zone>/')
@zone_default_ns.route('/<path:zone>/', defaults=dns_defaults)
@zone_ns.doc(params=zone_doc)
class Zone(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @zone_ns.response(200, 'Zone found.', model=entity_return_model)
    def get(self, configuration, view, zone):
        """
        Get a subzone belonging to default or provided Configuration and View plus Zone hierarchy.
        Subzones can be recursively retrieved by specifying extra "zones" parameters.
        Zones should be of the format:

        1. zone_name
        2. zone_name1/zones/subzone_name2/zones/subzone_name3
        """
        configuration = g.user.get_api().get_configuration(configuration)
        zone = generate_zone_fqdn(zone, configuration.get_view(view))
        if zone is None:
            return 'No matching Zone(s) found', 404
        return zone.to_json()

    @util.rest_workflow_permission_required('rest_page')
    def delete(self, configuration, view, zone):
        """
        Delete subzone belonging to default or provided Configuration and View plus Zone hierarchy.
        Subzones can be recursively retrieved by specifying extra "zones" parameters.
        Zones should be of the format:

        1. zone_name
        2. zone_name1/zones/subzone_name2/zones/subzone_name3
        """
        configuration = g.user.get_api().get_configuration(configuration)
        zone = generate_zone_fqdn(zone, configuration.get_view(view))
        if zone is None:
            return 'No matching Zone(s) found', 404
        zone.delete()
        return '', 204


@zone_ns.route('/hint/<string:hint>/')
@zone_default_ns.route('/hint/<string:hint>/', defaults=dns_defaults)
@zone_ns.doc()
class ZoneHintCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @zone_ns.response(200, 'Zone found.', model=entity_return_model)
    def get(self, configuration, view, hint):
        """
        Get a zone by hint belonging to default or provided Configuration and View.
        Zone hints should be of the format:

        1. abc
        2. abc.domain
        3. abc.domain.com
        """
        configuration = g.user.get_api().get_configuration(configuration)
        try:
            zones = se.get_zones_data_by_hint(configuration.get_id(), view, hint)
        except Exception:
            zones = None
        if zones == None or zones['status'] == 'FAIL':
            return 'No matching Zone(s) found', 404
        return_data = []
        for zone in zones['data']['select_field']:
            zone_object = g.user.get_api().get_entity_by_id(zone['id'])
            properties = ""
            for prop, value in zone_object.get_properties().items():
                properties += prop + "=" + value + "|"
            return_data.append({
                'id': zone['id'],
                'name': zone['txt'],
                'type': 'Zone',
                'properties': properties
            })

        return return_data


@host_ns.route('/hint/<string:host_hint>/')
@host_default_ns.route('/hint/<string:host_hint>/', defaults=dns_defaults)
@host_ns.doc()
class HostHintCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @host_ns.response(200, 'Host found.', model=entity_return_model)
    def get(self, host_hint, c, v):
        """
        Get a Host record by hint belonging to default or provided Configuration and View.
        Host hints should be of format:

        1. host name or same_as_zone
        2. fqdn

        Host hints can contain simple regex characters (^, $, *, ?)
        """
        start = 0
        count = 10
        host_records = []
        if host_hint == 'same_as_zone':
            options = 'retreiveFields=True'
        else:
            options = 'hint=%s|retreiveFields=true' % host_hint
        while True:
            results = g.user.get_api()._api_client.service.getHostRecordsByHint(
                start=start,
                count=count,
                options=options
            )
            for item in results:
                host_records.append(item)

            if len(results) == count:
                start += count
            else:
                break

        if len(host_records) == 0:
            return 'No matching Host Record(s) found', 404

        return host_records, 200


@zone_root_ns.route('/')
@zone_ns.route('/<path:zone>/zones/')
@zone_default_root_ns.route('/', defaults=dns_defaults)
@zone_default_ns.route('/<path:zone>/zones/', defaults=dns_defaults)
@zone_ns.doc(params=zone_doc)
class ZoneCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, view, zone=None):
        """
        Get all direct subzones belonging to default or provided Configuration and View plus Zone hierarchy.
        Subzones can be recursively retrieved by specifying extra "zones" parameters.
        Zones should be of the format:

        1. zone_name
        2. zone_name1/zones/zone_name2
        """
        configuration = g.user.get_api().get_configuration(configuration)
        zone_parent = configuration.get_view(view)
        leaf_zone = zone_parent
        if zone:
            zone_hierarchy = zone.split('/zones')
            zone_entity = zone_parent.get_zone(zone_hierarchy[0])
            leaf_zone = check_zone_in_path(zone_entity, zone_hierarchy[0], zone_hierarchy[1:], zone_parent)
            if leaf_zone is None:
                return 'No matching Zone(s) found', 404
        zones = leaf_zone.get_zones()
        result = [zone_entity.to_json() for zone_entity in zones]
        return jsonify(result)

    @util.rest_workflow_permission_required('rest_page')
    @zone_ns.response(200, 'Zone created.', model=entity_return_model)
    @zone_ns.expect(zone_model)
    def post(self, configuration, view, zone):
        """
        Create a zone or subzone belonging to default or provided Configuration and View plus Zone hierarchy.
        Subzones can be recursively retrieved by specifying extra "zones" parameters.
        Zones should be of the format:

        1. zone_name
        2. zone_name1/zones/zone_name2
        """
        data = entity_parser.parse_args()
        configuration = g.user.get_api().get_configuration(configuration)
        view = configuration.get_view(view)
        zone = generate_zone_fqdn(zone, view)
        if zone is None:
            return 'No matching Zone(s) found', 404
        zone_name = data['name']
        kwargs = util.properties_to_map(data['properties'])
        zone = view.add_zone('%s' % zone_name, **kwargs)
        return zone.to_json(), 201


def generate_zone_fqdn(zone=None, view=None, data=None):
    if view is not None:
        if zone is None:
            if data is not None:
                if 'absolute_name' in data.keys():
                    return data['absolute_name']
        elif '/zone' not in zone:
            zone_split = zone.split('.')
            zone_split.reverse()
            current = view
            for z in zone_split:
                current = current.get_zone(z)
            if data is not None:
                return data['absolute_name'].split('.')[0] + '.' + current.get_full_name()
            else:
                return current
        else:
            zone_parent = view
            zone_hierarchy = zone.split('/zones')
            zone_entity = zone_parent.get_zone(zone_hierarchy[0])
            zone = check_zone_in_path(zone_entity, zone_hierarchy[0], zone_hierarchy[1:], zone_parent)
            if data is not None:
                return data['absolute_name'].split('.')[0] + '.' + zone.get_full_name()
            else:
                return zone


def check_zone_in_path(zone_entity, pre_path, post_path, zone_parent, delimiter='/zones'):
    """Because "/" characters can be in the zone name, need to check if the "/" in the path is part of zone name or not
    """
    if not post_path:
        return zone_entity

    if zone_entity is not None:
        new_pre_path = post_path[0]
        if new_pre_path.startswith('/'):
            new_pre_path = new_pre_path[1:]
        sub_zone = zone_entity.get_zone(new_pre_path)
        final_result = check_zone_in_path(sub_zone, new_pre_path, post_path[1:], zone_entity)
        if final_result is not None:
            return final_result
    pre_path += delimiter + post_path.pop(0)

    zone = zone_parent.get_zone(pre_path)
    if zone is not None:
        final_result = check_zone_in_path(zone, pre_path, post_path, zone_parent)
        if final_result is not None:
            return final_result
    else:
        return None


@host_ns.route('/')
@host_zone_ns.route('/')
@host_default_ns.route('/', defaults=dns_defaults)
@host_zone_default_ns.route('/', defaults=dns_defaults)
class HostRecordCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @host_ns.response(201, 'Host Record successfully created.')
    def get(self, configuration, view, zone=None):
        """ Get all host records belonging to default or provided Configuration and View plus Zone hierarchy. """
        configuration = g.user.get_api().get_configuration(configuration)
        zone = generate_zone_fqdn(zone, configuration.get_view(view))
        host_records = zone.get_children_of_type(zone.HostRecord)
        result = [host.to_json() for host in host_records]
        return jsonify(result)

    @util.rest_workflow_permission_required('rest_page')
    @host_ns.response(201, 'Host Record successfully created.', model=entity_return_model)
    @host_ns.expect(host_model, validate=True)
    def post(self, configuration, view, zone=None):
        """ Create a host record belonging to default or provided Configuration and View plus Zone hierarchy. """
        data = host_parser.parse_args()
        configuration = g.user.get_api().get_configuration(configuration)
        view = configuration.get_view(view)
        absolute_name = generate_zone_fqdn(zone, view, data)
        ip4_address_list = data['ip4_address'].split(',')
        ttl = data.get('ttl', -1)
        properties = data.get('properties', '')
        host_record = view.add_host_record(absolute_name, ip4_address_list, ttl, properties)
        result = host_record.to_json()
        return result, 201


@external_host_ns.route('/')
class ExternalHostRecordCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @external_host_ns.response(201, 'External Host Record successfully created.', model=entity_return_model)
    @external_host_ns.expect(external_host_model, validate=True)
    def post(self, configuration, view):
        """ Create an external host record belonging to default or provided Configuration and View. """
        data = external_host_parser.parse_args()
        configuration = g.user.get_api().get_configuration(configuration)
        view = configuration.get_view(view)

        absolute_name = data.get('absolute_name', '')
        external_host_record = view.add_external_host_record(absolute_name)
        result = external_host_record.to_json()
        return result, 201


@external_host_ns.route('/<string:absolute_name>/')
@external_host_ns.doc(params=host_doc)
@external_host_default_ns.route('/<string:absolute_name>/', defaults=dns_defaults)
@external_host_default_ns.doc(params=absolute_name_doc)
@external_host_ns.response(200, 'External Host Record found.', model=entity_return_model)
class ExternalHostRecord(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, view, absolute_name):
        """ Get specified external host record belonging to default or provided Configuration and View plus Zone hierarchy. """
        config = g.user.get_api().get_configuration(configuration)
        view = config.get_view(view)

        host_record = view.get_external_host_record(absolute_name)
        if host_record is None:
            return 'No matching External Host Record(s) found', 404
        result = host_record.to_json()
        return jsonify(result)

    @util.rest_workflow_permission_required('rest_page')
    def delete(self, configuration, view, absolute_name):
        """
        Delete specified external host record belonging to default or provided Configuration and View plus Zone hierarchy.
        """
        config = g.user.get_api().get_configuration(configuration)
        view = config.get_view(view)

        try:
            host_record = view.get_external_host_record(absolute_name)
        except:
            host_record = None
        if host_record is None:
            return 'No matching External Host Record(s) found', 404
        host_record.delete()
        return '', 204


@host_ns.route('/<string:absolute_name>/')
@host_ns.doc(params=host_doc)
@host_default_ns.route('/<string:absolute_name>/', defaults=dns_defaults)
@host_default_ns.doc(params=absolute_name_doc)
@host_ns.response(200, 'Host Record found.', model=entity_return_model)
class HostRecord(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, view, absolute_name):
        """ Get specified host record belonging to default or provided Configuration and View plus Zone hierarchy. """
        config = g.user.get_api().get_configuration(configuration)
        view = config.get_view(view)

        host_record = view.get_host_record(absolute_name)
        if host_record is None:
            return 'No matching Host Record(s) found', 404
        result = host_record.to_json()
        return jsonify(result)

    @util.rest_workflow_permission_required('rest_page')
    def delete(self, configuration, view, absolute_name):
        """
        Delete specified host record belonging to default or provided Configuration and View plus Zone hierarchy.
        """
        config = g.user.get_api().get_configuration(configuration)
        view = config.get_view(view)

        host_record = view.get_host_record(absolute_name)
        if host_record is None:
            return 'No matching Host Record(s) found', 404
        host_record.delete()
        return '', 204

    @util.rest_workflow_permission_required('rest_page')
    @host_ns.expect(host_patch_model, validate=True)
    def patch(self, configuration, view, absolute_name):
        """
        Update specified host record belonging to default or provided Configuration and View plus Zone hierarchy.
        """
        data = host_patch_parser.parse_args()
        configuration = g.user.get_api().get_configuration(configuration)
        view = configuration.get_view(view)

        absolute_name = data.get('absolute_name', absolute_name)
        host_record = view.get_host_record(absolute_name)
        if host_record is None:
            return 'No matching Host Record(s) found', 404
        if data['properties'] is not None:
            properties = data.get('properties')
            host_record._properties = util.properties_to_map(properties)
        if data['ip4_address'] is not None:
            host_record.set_property('addresses', data['ip4_address'])
        if data['ttl'] is not None:
            host_record.set_property('ttl', str(data.get('ttl')))
        if data['name'] is not None:
            host_record.name = data.get('name')
        host_record.update()
        result = host_record.to_json()
        return result


@cname_zone_ns.route('/')
@cname_zone_default_ns.route('/', defaults=dns_defaults)
class CNameRecordCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @cname_ns.response(200, 'Found CName records.')
    def get(self, configuration, view, zone=None):
        """ Get all cname records belonging to default or provided Configuration and View plus Zone hierarchy. """
        configuration = g.user.get_api().get_configuration(configuration)
        zone = generate_zone_fqdn(zone, configuration.get_view(view))
        if zone is None:
            return 'No matching Zone(s) found', 404

        host_records = zone.get_children_of_type(zone.AliasRecord)
        result = [host.to_json() for host in host_records]
        return jsonify(result)

    @util.rest_workflow_permission_required('rest_page')
    @cname_ns.response(201, 'CName Record successfully created.', model=entity_return_model)
    @cname_ns.expect(cname_model, validate=True)
    def post(self, configuration, view, zone=None):
        """ Create a cname record belonging to default or provided Configuration and View plus Zone hierarchy. """
        data = cname_parser.parse_args()
        configuration = g.user.get_api().get_configuration(configuration)
        view = configuration.get_view(view)
        absolute_name = generate_zone_fqdn(zone, view, data)
        ip4_address_list = data['linked_record']
        ttl = data.get('ttl', -1)
        properties = data.get('properties', '')
        cname_record = view.add_alias_record(absolute_name, ip4_address_list, ttl, properties)
        result = cname_record.to_json()
        return result, 201


@cname_ns.route('/<string:absolute_name>/')
@cname_ns.doc(params=host_doc)
@cname_default_ns.route('/<string:absolute_name>/', defaults=dns_defaults)
@cname_default_ns.doc(params=absolute_name_doc)
@cname_ns.response(200, 'CName Record found.', model=entity_return_model)
class CNameRecord(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, view, absolute_name):
        """ Get specified cname record belonging to default or provided Configuration and View plus Zone hierarchy. """
        config = g.user.get_api().get_configuration(configuration)
        view = config.get_view(view)

        cname_record = view.get_alias_record(absolute_name)
        if cname_record is None:
            return 'No matching CName Record(s) found', 404
        result = cname_record.to_json()
        return jsonify(result)

    @util.rest_workflow_permission_required('rest_page')
    def delete(self, configuration, view, absolute_name):
        """
        Delete specified cname record belonging to default or provided Configuration and View plus Zone hierarchy.
        """
        config = g.user.get_api().get_configuration(configuration)
        view = config.get_view(view)

        cname_record = view.get_alias_record(absolute_name)
        if cname_record is None:
            return 'No matching CName Record(s) found', 404
        cname_record.delete()
        return '', 204

    @util.rest_workflow_permission_required('rest_page')
    @cname_ns.expect(cname_patch_model, validate=True)
    def patch(self, configuration, view, absolute_name):
        """
        Update specified cname record belonging to default or provided Configuration and View plus Zone hierarchy.
        """
        data = cname_patch_parser.parse_args()
        configuration = g.user.get_api().get_configuration(configuration)
        view = configuration.get_view(view)

        absolute_name = data.get('absolute_name', absolute_name)
        cname_record = view.get_alias_record(absolute_name)
        if cname_record is None:
            return 'No matching CName Record(s) found', 404
        if data['properties'] is not None:
            properties = data.get('properties')
            cname_record._properties = util.properties_to_map(properties)
        if data['linked_record'] is not None:
            cname_record.set_property('linkedRecordName', data['linked_record'])
        if data['ttl'] is not None:
            cname_record.set_property('ttl', str(data.get('ttl')))
        if data['name'] is not None:
            cname_record.name = data['name']

        cname_record.update()
        result = cname_record.to_json()
        return result


@zone_ns.route('/<path:zone>/option_name/<string:option_name>/server/<path:server_id>/deployment_options/')
@zone_default_ns.route(
    '/<path:zone>/option_name/<string:option_name>/server/<path:server_id>/deployment_options/', defaults=dns_defaults)
@view_ns.route('/<string:view>/option_name/<string:option_name>/server/<path:server_id>/deployment_options/')
@view_default_ns.route(
    '/<string:view>/option_name/<string:option_name>/server/<path:server_id>/deployment_options/',
    defaults=config_defaults
)
class DeploymentOptionCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, option_name, server_id, view=None, zone=None):
        """
        Find a deployment option set on the View or Zone, by name and assigned server ID

        Server ID can be:

        1. 0 if the option is set to All Servers
        2. The entity ID of the assigned server or server group
        3. -1 if you are not sure which of the above to use
        """
        configuration = g.user.get_api().get_configuration(configuration)
        if zone:
            zone = generate_zone_fqdn(zone, configuration.get_view(view))
            return get_option(zone, option_name, int(server_id))
        elif view:
            view = configuration.get_view(view)
            return get_option(view, option_name, int(server_id))


    @util.rest_workflow_permission_required('rest_page')
    def delete(self, configuration, option_name, server_id, view=None, zone=None):
        """
        Delete a deployment option set on the configuration, by name and assigned server ID

        Server ID can be:

        1. 0 if the option is set to All Servers
        2. The entity ID of the assigned server or server group
        """
        configuration = g.user.get_api().get_configuration(configuration)
        if int(server_id) < 0:
            return 'Server ID must be 0 or higher for delete function', 400

        if zone:
            zone = generate_zone_fqdn(zone, configuration.get_view(view))
            return del_option(zone, option_name, int(server_id))
        elif view:
            view = configuration.get_view(view)
            return del_option(view, option_name, int(server_id))


@zone_ns.route('/<path:zone>/deployment_options/')
@zone_default_ns.route('/<path:zone>/deployment_options/', defaults=dns_defaults)
@view_ns.route('/<string:view>/deployment_options/')
@view_default_ns.route('/<string:view>/deployment_options/', defaults=config_defaults)
class DeploymentOption(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @zone_ns.expect(deployment_option_post_model, validate=True)
    @zone_default_ns.expect(deployment_option_post_model, validate=True)
    @view_ns.expect(deployment_option_post_model, validate=True)
    @view_default_ns.expect(deployment_option_post_model, validate=True)
    def post(self, configuration, view=None, zone=None):
        """
        Add a DNS Deployment Option to a view or zone
        """
        configuration = g.user.get_api().get_configuration(configuration)
        data = deployment_option_post_parser.parse_args()
        if zone:
            zone = generate_zone_fqdn(zone, configuration.get_view(view))
            return add_option(zone, data)
        elif view:
            view = configuration.get_view(view)
            return add_option(view, data)


@zone_ns.route('/<path:zone>/server/<path:server_fqdn>/deployment_roles/')
@zone_default_ns.route('/<path:zone>/server/<path:server_fqdn>/deployment_roles/', defaults=dns_defaults)
@view_ns.route('/<string:view>/server/<path:server_fqdn>/deployment_roles/')
@view_default_ns.route('/<string:view>/server/<path:server_fqdn>/deployment_roles/',defaults=config_defaults)
class DeploymentRoleCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, server_fqdn, view=None, zone=None):
        """
        Find a Deployment Role set on the View or Zone, by the assigned server interface
        """
        configuration = g.user.get_api().get_configuration(configuration)
        if zone:
            zone = generate_zone_fqdn(zone, configuration.get_view(view))
            return get_role(zone, 'dns', server_fqdn)
        elif view:
            view = configuration.get_view(view)
            return get_role(view, 'dns', server_fqdn)

    @util.rest_workflow_permission_required('rest_page')
    def delete(self, configuration, server_fqdn, view=None, zone=None):
        """
        Delete a Deployment Role set on the configuration, by the assigned server interface
        """
        configuration = g.user.get_api().get_configuration(configuration)

        if zone:
            zone = generate_zone_fqdn(zone, configuration.get_view(view))
            return del_role(zone, 'dns', server_fqdn)
        elif view:
            view = configuration.get_view(view)
            return del_role(view, 'dns', server_fqdn)


@zone_ns.route('/<path:zone>/deployment_roles/')
@zone_default_ns.route('/<path:zone>/deployment_roles/', defaults=dns_defaults)
@view_ns.route('/<string:view>/deployment_roles/')
@view_default_ns.route('/<string:view>/deployment_roles/', defaults=config_defaults)
class DeploymentRole(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @zone_ns.expect(deployment_role_post_model, validate=True)
    @zone_default_ns.expect(deployment_role_post_model, validate=True)
    @view_ns.expect(deployment_role_post_model, validate=True)
    @view_default_ns.expect(deployment_role_post_model, validate=True)
    def post(self, configuration, view=None, zone=None):
        """
        Add a DNS Deployment Role to a view or zone
        """
        configuration = g.user.get_api().get_configuration(configuration)
        data = deployment_role_post_parser.parse_args()
        if zone:
            zone = generate_zone_fqdn(zone, configuration.get_view(view))
            return add_role(zone, data)
        elif view:
            view = configuration.get_view(view)
            return add_role(view, data)
