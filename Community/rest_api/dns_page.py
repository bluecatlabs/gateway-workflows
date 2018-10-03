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
import config.default_config as config
from .configuration_page import config_doc, config_defaults, entity_parser, entity_model, entity_return_model
from main_app import api


view_default_ns = api.namespace('views', path='/views/', description='View operations')
view_ns = api.namespace('views', path='/configurations/<string:configuration>/views/', description='View operations')

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

host_parser = reqparse.RequestParser()
host_parser.add_argument('absolute_name', location="json", required=True, help='The FQDN of the record')
host_parser.add_argument(
    'ip4_address',
    location="json",
    required=True,
    help='The IPv4 addresses associated with the host record',
)
host_parser.add_argument('ttl', type=int, location="json", help='The TTL of the record')
host_parser.add_argument('properties', location="json", help='The properties of the record')

host_patch_parser = host_parser.copy()
host_patch_parser.replace_argument(
    'ip4_address',
    location="json",
    required=False,
    help='The IPv4 addresses associated with the host record',
)
host_patch_parser.remove_argument('absolute_name')

cname_parser = host_parser.copy()
cname_parser.remove_argument('ip4_address')
cname_parser.add_argument('linked_record', location="json", help='The name of the record to which this alias will link')

cname_patch_parser = cname_parser.copy()
cname_patch_parser.remove_argument('absolute_name')

zone_model = api.clone(
    'zones',
    entity_model
)

host_model = api.model(
    'host_records',
    {
        'absolute_name': fields.String(required=True, description='The FQDN of the host record'),
        'ip4_address':  fields.String(description='The IPv4 addresses associated with the host record'),
        'ttl':  fields.Integer(description='The TTL of the host record'),
        'properties':  fields.String(description='The properties of the host record', default='attribute=value|'),
    },
)

host_patch_model = api.model(
    'host_records_patch',
    {
        'ip4_address':  fields.String(description='The IPv4 addresses associated with the host record'),
        'ttl':  fields.Integer(description='The TTL of the host record'),
        'properties':  fields.String(description='The properties of the host record', default='attribute=value|'),
    },
)

cname_model = api.model(
    'cname_records',
    {
        'absolute_name': fields.String(required=True, description='The FQDN of the CName record'),
        'linked_record':  fields.String(
            required=True,
            description='The name of the record to which this alias will link',
        ),
        'ttl':  fields.Integer(description='The TTL of the CName record'),
        'properties':  fields.String(description='The properties of the CName record', default='attribute=value|'),
    },
)

cname_patch_model = api.model(
    'cname_records_patch',
    {
        'linked_record':  fields.String(description='The name of the record to which this alias will link'),
        'ttl':  fields.Integer(description='The TTL of the CName record'),
        'properties':  fields.String(description='The properties of the CName record', default='attribute=value|'),
    },
)

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
        zone_parent = configuration.get_view(view)
        zone_hierarchy = zone.split('/zones')
        zone_entity = zone_parent.get_zone(zone_hierarchy[0])
        zone = check_zone_in_path(zone_entity, zone_hierarchy[0], zone_hierarchy[1:], zone_parent)
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
        zone_parent = configuration.get_view(view)
        zone_hierarchy = zone.split('/zones')
        zone_entity = zone_parent.get_zone(zone_hierarchy[0])
        zone = check_zone_in_path(zone_entity, zone_hierarchy[0], zone_hierarchy[1:], zone_parent)
        if zone is None:
            return 'No matching Zone(s) found', 404
        zone.delete()
        return '', 204


@zone_ns.route('/<path:zone>/zones/')
@zone_default_ns.route('/<path:zone>/zones/', defaults=dns_defaults)
@zone_ns.doc(params=zone_doc)
class ZoneCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, view, zone):
        """
        Get all direct subzones belonging to default or provided Configuration and View plus Zone hierarchy.
        Subzones can be recursively retrieved by specifying extra "zones" parameters.
        Zones should be of the format:

        1. zone_name
        2. zone_name1/zones/zone_name2
        """
        configuration = g.user.get_api().get_configuration(configuration)
        zone_parent = configuration.get_view(view)
        zone_hierarchy = zone.split('/zones')
        zone_entity = zone_parent.get_zone(zone_hierarchy[0])
        zone = check_zone_in_path(zone_entity, zone_hierarchy[0], zone_hierarchy[1:], zone_parent)
        if zone is None:
            return 'No matching Zone(s) found', 404
        zones = zone.get_zones()
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
        zone_parent = view
        zone_hierarchy = zone.split('/zones')
        zone_entity = zone_parent.get_zone(zone_hierarchy[0])
        zone = check_zone_in_path(zone_entity, zone_hierarchy[0], zone_hierarchy[1:], zone_parent)
        if zone is None:
            return 'No matching Zone(s) found', 404
        zone_name = data['name']
        kwargs = util.properties_to_map(data['properties'])
        zone = view.add_zone('%s.%s' % (zone_name, zone.get_full_name()), **kwargs)
        return zone.to_json(), 201


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
        view = configuration.get_view(view)
        zone_parent = view
        zone_hierarchy = zone.split('/zones')
        zone_entity = zone_parent.get_zone(zone_hierarchy[0])
        zone = check_zone_in_path(zone_entity, zone_hierarchy[0], zone_hierarchy[1:], zone_parent)

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

        if zone is None:
            absolute_name = data['absolute_name']
        else:
            zone_parent = view
            zone_hierarchy = zone.split('/zones')
            zone_entity = zone_parent.get_zone(zone_hierarchy[0])
            zone = check_zone_in_path(zone_entity, zone_hierarchy[0], zone_hierarchy[1:], zone_parent)
            absolute_name = data['absolute_name'] + '.' + zone.get_full_name()
        ip4_address_list = data['ip4_address'].split(',')
        ttl = data.get('ttl', -1)
        properties = data.get('properties', '')
        host_record = view.add_host_record(absolute_name, ip4_address_list, ttl, properties)
        result = host_record.to_json()
        return result, 201


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
            host_record.properties = util.properties_to_map(properties)
        if data['ip4_address'] is not None:
            host_record.set_property('addresses', data['ip4_address'])
        if data['ttl'] is not None:
            host_record.set_property('ttl', str(data.get('ttl')))
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
        view = configuration.get_view(view)
        if zone is None:
            return 'No matching Zone(s) found', 404
        zone_parent = view
        zone_hierarchy = zone.split('/zones')
        zone_entity = zone_parent.get_zone(zone_hierarchy[0])
        zone = check_zone_in_path(zone_entity, zone_hierarchy[0], zone_hierarchy[1:], zone_parent)

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

        if zone is None:
            absolute_name = data['absolute_name']
        else:
            zone_parent = view
            zone_hierarchy = zone.split('/zones')
            zone_entity = zone_parent.get_zone(zone_hierarchy[0])
            zone = check_zone_in_path(zone_entity, zone_hierarchy[0], zone_hierarchy[1:], zone_parent)
            absolute_name = data['absolute_name'] + '.' + zone.get_full_name()
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
            cname_record.properties = util.properties_to_map(properties)
        if data['linked_record'] is not None:
            cname_record.set_property('linkedRecordName', data['linked_record'])
        if data['ttl'] is not None:
            cname_record.set_property('ttl', str(data.get('ttl')))

        cname_record.update()
        result = cname_record.to_json()
        return result

