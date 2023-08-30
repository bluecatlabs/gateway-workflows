# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
import os
import json
import traceback

from flask import g
from urllib.parse import quote

from bluecat_libraries.http_client import ClientError
from bluecat_libraries.address_manager.apiv2.client import Client

from .constants import DEFAULT_FIELDS

from ..common import common
from ..common.exception import (
    NotSupportedRestV2,
    RESTv2ResponseException
)
from ..common.roles import get_service_interfaces_and_zone_transfer_interface, get_API_formatted_role
from ..rest_v2.common import get_view_of_zone


class RESTv2:
    # TODO: define constant list for media_type
    def __init__(self, media_type='application/hal+json'):
        """
        ``verify`` has the same meaning as arguments of the same name commonly found in
        ``requests`` functions.
        """
        # validate bam
        bam_api_version = '1'
        v = os.environ.get("BAM_API_VERSION")
        if v is not None:
            try:
                bam_api_version = int(v)
            except ValueError:
                pass
        version = g.user.get_api().get_version() if bam_api_version == '1' else g.user.bam_api.v2.bam_version
        if version < '9.5.0':
            raise NotSupportedRestV2(version)
        if g.user and g.user.bam_api.v2:
            self.v2_client = g.user.bam_api.v2
        else:
            self.v2_client = Client(url=g.user.get_api_netloc(), verify=False)
            self.v2_client.auth = 'Basic ' + g.user.session_auth

        self.media_type = media_type
        self.headers = {
            'accept': media_type,
        }
        # TODO: update to use 1 fields
        self.fields = DEFAULT_FIELDS
        self.field = {'fields': DEFAULT_FIELDS}
        self.expected_status_code = [200, 201, 204]

    @property
    def is_authenticated(self) -> bool:
        """
        Determine whether the authentication necessary to communicate with BlueCat Address
        Manager is set.
        """
        return self.v2_client.is_authenticated

    def _require_auth(self):
        """
        Raise exception if the client does not have the necessary authentication
        set to communicate with the target service.
        """
        if not self.is_authenticated:
            raise ClientError("Use of this method requires authentication.")

    def get_headers(self, get_links):
        headers = self.headers
        if not get_links:
            headers = {
                'accept': 'application/json',
            }
        return headers

    def get_entity_by_id(self, entity_id, get_links=True):
        """
        GET Entity by ID
        :param entity_id: ID of entity.
        :param get_links: True/False.
        """
        self._require_auth()
        headers = self.get_headers(get_links)
        response = self.v2_client.http_get("?filter=id:{}".format(entity_id), headers=headers)
        return response.get('data', [])[0] if response.get('data', []) else {}

    def get_entity_by_name(self, name, get_links=True):
        """
        GET Entity by name
        :param name: name of entity.
        :param get_links: True/False.
        """
        headers = self.get_headers(get_links)
        self._require_auth()
        response = self.v2_client.http_get("?filter=name:'{}'".format(name), headers=headers)
        return response

    def get_v2(self, filter='', fields=''):
        """
        v2
        :param filter:
        :param fields:
        """
        self._require_auth()
        if not fields:
            fields = "id,name,type,_links"
        response = self.v2_client.http_get("?fields={}&filter={}".format(fields, filter))
        return response

    def link_api(self, _link, fields=''):
        if not fields:
            fields = "id,name,type,_links"
        _link = _link.replace('/api/v2', '')
        response = self.v2_client.http_get(_link + "?fields={}".format(fields),
                                           expected_status_codes=self.expected_status_code)
        return response

    def get_blocks(self, filters='', fields=''):
        if not fields:
            fields = self.fields + ",range"
        query_string = '?fields={}'.format(fields)
        if filters:
            query_string += "&filter={}".format(filters)
        self._require_auth()
        response = self.v2_client.http_get(
            "/blocks" + query_string, expected_status_codes=self.expected_status_code)
        return response

    def get_networks(self, filters='', fields=''):
        if not fields:
            fields = self.fields + ",range"
        query_string = '?fields={}'.format(fields)
        if filters:
            query_string += "&filter={}".format(filters)
        self._require_auth()
        response = self.v2_client.http_get(
            "/networks" + query_string, expected_status_codes=self.expected_status_code)
        return response

    def get_block_by_range(self, network_range, filter='', fields=''):
        if not fields:
            fields = self.fields + ",_links,range"
        response = self.v2_client.http_get(
            "/blocks" + "?filter={} and range:'{}'&fields={}".format(filter, network_range, fields),
            expected_status_codes=self.expected_status_code)
        return response

    def get_network_by_range(self, block_range, filter='', fields=''):
        if not fields:
            fields = self.fields + ",_links,range"
        response = self.v2_client.http_get(
            "/networks" + "?filter={} and range:'{}'&fields={}".format(filter, block_range, fields),
            expected_status_codes=self.expected_status_code)
        return response

    def add_deployment_option(self, collection, collection_id, json_data, get_links=False):
        value = json_data.get('value')
        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], list):
            for policy_list in value:
                if not policy_list:
                    continue
                if policy_list[-1].lower() in ('default', 'any'):
                    policy_list[-1] = policy_list[-1].lower()
                else:
                    policy_list[-1] = policy_list[-1].upper()

        headers = self.get_headers(get_links)
        response = self.v2_client.http_post(
            "/{}/{}/deploymentOptions".format(collection, collection_id),
            json=json_data, headers=headers, expected_status_codes=self.expected_status_code)
        return response

    def get_deployment_option_by_collection(self, collection, collection_id, filter='', fields=''):
        if not fields:
            fields = "id,name,type,_links,range,value"
        response = self.v2_client.http_get(
            "/{}/{}/deploymentOptions".format(collection, collection_id) +
            "?filter={}&fields={}".format(filter, fields), expected_status_codes=self.expected_status_code)
        return response

    def delete_deployment_option(self, option_id):
        response = self.v2_client.http_delete("/deploymentOptions/{}".format(option_id),
                                              expected_status_codes=self.expected_status_code)
        return response

    def make_response(self, response):
        if response.status_code not in [200, 201, 204]:
            raise RESTv2ResponseException(response.content.decode('utf-8'))
        json_data = response.json()
        return json_data

    def get_configurations(self):
        """
        GET all Configurations
        """
        self._require_auth()
        response = self.v2_client.http_get('/configurations', params=self.field)
        return response

    def get_configuration(self, configuration_id):
        """
        GET configuration by ID
        :param configuration_id: ID of configuration.
        """
        self._require_auth()
        response = self.v2_client.http_get('/configurations/{}'.format(configuration_id), params=self.field)
        return response

    def get_configuration_by_name(self, configuration_name):
        """
        GET configuration by name
        :param configuration_name: Name of configuration.
        """
        self._require_auth()
        response = self.v2_client.http_get(
            "/configurations?filter=name:'{}'".format(configuration_name), params=self.field,
            expected_status_codes=[200, 201, 204])
        if response['count'] == 0:
            raise ClientError("Configuration named {} not found".format(configuration_name))
        return response

    def get_views(self):
        """
        GET all Views
        """
        self._require_auth()
        response = self.v2_client.http_get('/views')
        return response

    def get_view_by_id(self, view_id):
        """
        GET view by ID
        :param view_id: ID of view.
        """
        self._require_auth()
        response = self.v2_client.http_get('/views/{}'.format(view_id))
        return response

    def get_view_by_name(self, view_name, filter='', fields=''):
        """
        GET view by name
        :param view_name: Name of view.
        """
        self._require_auth()
        if not fields:
            fields = self.fields
        filters = "name:'{}'".format(view_name)
        if filter:
            filters += 'and ' + filter
        response = self.v2_client.http_get("/views?filter={}&field={}".format(filters, fields))
        if response['count'] == 0:
            raise ClientError("View named {} not found".format(view_name))
        return response

    def get_views_in_configuration(self, configuration_id):
        """
        GET views in configuration
        :param configuration_id: ID of configuration.
        """
        self._require_auth()
        response = self.v2_client.http_get("/configurations/{}/views".format(str(configuration_id)))
        return response

    def get_zones(self, filters='', fields=''):
        """
        GET all zones
        """
        query_string = "?"
        if not fields:
            fields = self.fields + ', absoluteName'
        query_string += 'fields={}'.format(fields)
        if filters:
            query_string += "&filter={} and type:ne('ExternalHostsZone')".format(filters)
        self._require_auth()
        response = self.v2_client.http_get('/zones' + query_string)
        return response

    def get_zones_in_configuration(self, configuration_id):
        """
        GET all zones
        """
        self._require_auth()
        response = self.v2_client.http_get('/zones?filter=ancestor.id: {}'.format(configuration_id))
        return response

    def get_zone(self, zone_id):
        """
        GET zone by ID
        :param zone_id: ID of zone.
        """
        self._require_auth()
        response = self.v2_client.http_get('/zones/{}'.format(zone_id))
        return response

    def get_zone_by_name(self, zone_name, filter='', fields=''):
        """
        GET zone by absolute name
        :param zone_name: Absolute name of zone.
        """
        self._require_auth()
        if not fields:
            fields = self.fields
        filters = "absoluteName:'{}'".format(zone_name)
        if filter:
            filters += " and {}".format(filter)
        response = self.v2_client.http_get("/zones?filter={}&field={}".format(filters, fields))
        if response['count'] == 0:
            raise ClientError("Zone named {} not found".format(zone_name))
        return response

    def get_zones_in_view(self, view_id):
        """
        GET zones in view
        :param view_id: ID of view.
        """
        self._require_auth()
        response = self.v2_client.http_get("/views/{}/zones".format(str(view_id)))
        return response

    def get_subzones_in_zone(self, zone_id):
        """
        GET subzones in zone
        :param zone_id: ID of zone.
        """
        self._require_auth()
        response = self.v2_client.http_get("/zones/{}/zones".format(str(zone_id)))
        return response

    def get_collection(self, entity_obj):
        links = entity_obj.get("_links")
        if not links:
            # TODO: please ignore if object not has _link
            raise ClientError("Invalid input")
        link = links.get("collection")["href"]
        # collection_link = link[:link.rfind(entity_obj.get("type").lower())]
        return link

    def get_servers(self):
        """
        GET all Servers
        """
        self._require_auth()
        response = self.v2_client.http_get('/servers')
        return response

    def get_server(self, server_id):
        """
        GET server by ID
        :param server_id: ID of server.
        """
        self._require_auth()
        response = self.v2_client.http_get('/servers/{}'.format(server_id))
        return response

    def get_servers_in_configuration(self, configuration_id):
        """
        GET servers in configuration
        :param configuration_id: ID of configuration.
        """
        self._require_auth()
        response = self.v2_client.http_get("/configurations/{}/servers".format(str(configuration_id)))
        return response

    def get_server_by_name(self, server_name):
        """
        GET servers by name
        :param server_name: name of server.
        """
        self._require_auth()
        response = self.v2_client.http_get("/servers?filter=name:'{}'".format(str(server_name)))
        if response['count'] == 0:
            raise ClientError("Server named {} not found".format(server_name))
        return response

    def get_server_by_name_in_configuration(self, configuration_id, server_name):
        """
        GET servers by name
        :param configuration_id: id of configuration.
        :param server_name: name of server.
        """
        self._require_auth()
        response = self.v2_client.http_get("/configurations/{}/servers?filter=name:'{}'".
                                    format(configuration_id, str(server_name)))
        if response['count'] == 0:
            raise ClientError("Server named {} not found".format(server_name))
        return response

    def get_deployment_role_interfaces(self, role_id, fields=''):
        self._require_auth()
        if not fields:
            fields = self.fields + ', configuration, server, deploymentRoleInterfaceType'
        response = self.v2_client.http_get("/deploymentRoles/{}/interfaces?fields={}".format(role_id, fields))
        return response

    def get_deployment_roles(self, role_type_filter, interface_included=True):
        """
        GET all roles
        """
        filter_role = {
            'filter': role_type_filter
        }
        self._require_auth()
        response = self.v2_client.http_get('/deploymentRoles', params=filter_role)
        result = response
        if interface_included and result.get('data'):
            for role in result.get('data'):
                service_interface, zone_transfer_interface = get_service_interfaces_and_zone_transfer_interface(
                    role.get('id'))
                role.update({
                    'serverInterface': service_interface,
                    'zoneTransferServerInterface': zone_transfer_interface
                })
        return result

    def get_deployment_role(self, deployment_role_id, interface_included=True):
        """
        GET deployment role by ID
        :param deployment_role_id: ID of deployment role.
        :param interface_included: whether load role interfaces or not
        """
        self._require_auth()
        response = self.v2_client.http_get('/deploymentRoles/{}'.format(deployment_role_id))
        data = response
        if interface_included and data:
            service_interface, zone_transfer_interface = get_service_interfaces_and_zone_transfer_interface(
                data.get('id'))
            data.update({
                'serverInterface': service_interface,
                'zoneTransferServerInterface': zone_transfer_interface
            })

        return data

    def update_dns_deployment_role(self, role_id, role):
        """
        Update deployment role
        :param role_id: ID of role
        :param role: DNS Deployment role data
        """
        self._require_auth()
        headers = {
            'accept': 'application/hal+json',
            'Content-Type': 'application/hal+json',
        }
        role = get_API_formatted_role(role)
        response = self.v2_client.http_put(
            '/deploymentRoles/{}'.format(role_id), headers=headers, data=json.dumps(role),
            expected_status_codes=self.expected_status_code)
        return response

    def get_deployment_roles_by_server(self, server_id, role_filter, interface_included=True):
        """
        GET deployment roles by server
        :param server_id: id of server
        :param role_filter: filter string for roles
        :param interface_included: whether you get roles' interfaces
        """
        filter_role = {
            'filter': role_filter
        }
        self._require_auth()
        response = self.v2_client.http_get("/servers/{}/deploymentRoles".format(str(server_id)), params=filter_role)
        result = response
        if interface_included and result.get('data'):
            for role in result.get('data'):
                service_interface, zone_transfer_interface = get_service_interfaces_and_zone_transfer_interface(
                    role.get('id'))
                role.update({
                    'serverInterface': service_interface,
                    'zoneTransferServerInterface': zone_transfer_interface
                })
        return result

    def get_deployment_roles_by_collection(self, collection, collection_id, filters='', interface_included=True):
        """
        GET deployment roles by collection
        :param collection: name of collection
        :param collection_id: ID of collection
        :param filters: Optional filters
        :param interface_included: whether you get deployment roles' interfaces
        """
        self._require_auth()
        response = self.v2_client.http_get(
            "/{}/{}/deploymentRoles".format(str(collection), str(collection_id))
            + ('?filter={}'.format(filters) if filters else ''))
        result = response
        if interface_included and result.get('data'):
            for role in result.get('data'):
                service_interface, zone_transfer_interface = get_service_interfaces_and_zone_transfer_interface(
                    role.get('id'))
                role.update({
                    'serverInterface': service_interface,
                    'zoneTransferServerInterface': zone_transfer_interface
                })
        return result

    def get_deployment_options(self):
        """
        GET all Servers
        """
        self._require_auth()
        response = self.v2_client.http_get('/deploymentOptions')
        return response

    def get_deployment_option(self, deployment_option_id):
        """
        GET deployment option by ID
        :param deployment_option_id: ID of deployment option.
        """
        self._require_auth()
        response = self.v2_client.http_get('/deploymentOptions/{}'.format(deployment_option_id))
        return response

    def get_deployment_options_by_collection(self, collection, collection_id):
        """
        GET deployment options by collection
        :param collection: name of collection.
        :param collection_id: ID of collection.
        """
        self._require_auth()
        response = self.v2_client.http_get(
            "/{}/{}/deploymentOptions".format(str(collection), str(collection_id)))
        return response

    def get_link_entity(self, href):
        """
        GET entity by href
        :param href: hypertext reference of entity
        """
        self._require_auth()
        response = self.v2_client.http_get("/{}".format(href))
        return response

    def get_interface(self, interface_id):
        """
        GET server interface by ID
        :param interface_id: ID of interface id.
        """
        self._require_auth()
        response = self.v2_client.http_get('/interfaces/{}'.format(interface_id))
        return response

    def get_interfaces(self):
        """
        GET all Servers Interfaces
        """
        self._require_auth()
        response = self.v2_client.http_get('/interfaces')
        return response

    def get_server_interfaces(self, server_id):
        """
        GET all Servers Interfaces
        """
        self._require_auth()
        response = self.v2_client.http_get('/servers/{}/interfaces'.format(server_id))
        return response

    def get_interfaces_in_configuration(self, configuration_id):
        """
        GET all Servers Interfaces
        """
        self._require_auth()
        response = []
        servers = self.get_servers_in_configuration(configuration_id).get('data')
        for server in servers:
            response.extend(self.get_server_interfaces(server.get('id')).get('data'))
        return {
            'count': len(response),
            'data': response
        }

    def get_interface_by_name(self, interface_name, filter='', fields=''):
        """
        GET servers by name
        :param interface_name: name of server interface.
        """
        self._require_auth()
        if not fields:
            fields = self.fields + ', server'
        filter = filter + "and name:'{}'".format(interface_name) if filter else "name:'{}'".format(interface_name)
        response = self.v2_client.http_get("/interfaces?filter={}&fields={}".format(filter, fields))
        if response['count'] == 0:
            raise ClientError("Interface named {} not found".format(interface_name))
        return response

    def get_deployment_roles_in_configuration(self, configuration_id, role_filter):
        """
        GET all Servers Interfaces
        """
        self._require_auth()
        response = []
        servers = self.get_servers_in_configuration(configuration_id).get('data')
        for server in servers:
            response.extend(self.get_deployment_roles_by_server(server.get('id'), role_filter).get('data'))
        return {
            'count': len(response),
            'data': response
        }

    def delete_deployment_role(self, role_id):
        """
        DELETE selected deployment role
        :param role_id: name of server.
        """
        self._require_auth()
        response = self.v2_client.http_delete("/deploymentRoles/{}".format(str(role_id)), expected_status_codes=[204])
        return response

    def add_dns_deployment_role(self, role, collection, collection_id):
        """
        ADD deployment role
        :param role: DNS Deployment role.
        :param collection: collection of deployment role.
        :param collection_id: collection ID of deployment role.
        """
        self._require_auth()
        headers = {
            'accept': 'application/hal+json',
            'Content-Type': 'application/hal+json',
        }
        role = get_API_formatted_role(role)
        response = self.v2_client.http_post(
            '/{}/{}/deploymentRoles'.format(collection, collection_id), headers=headers,
            data=json.dumps(role))
        return response

    def get_views_by_hint(self, ancestor_id, hint='', limit=10, fields=''):
        """
        GET views start with hint in an ancestor
        :param ancestor_id: ancestor id which contains the views searched
        :param hint: hint which views start with
        :param limit: number of result
        :param fields: fields including in response data
        """
        self._require_auth()
        if not fields:
            fields = self.fields
        # Encoding for special character in hint
        encoded_hint = quote(f"{hint}".encode('utf-8'))
        query_params_str = f"fields={fields}&filter=ancestor.id:{ancestor_id} and name:startsWith('{encoded_hint}')&limit={limit}&total=true"
        response = self.v2_client.http_get(f"/views?{query_params_str}", expected_status_codes=self.expected_status_code)
        return response

    def get_view_in_configuration_by_name(self, configuration_id, view_name, fields=''):
        """
        GET view by name in configuration_id
        :param configuration_id: configuration id which contains the view
        :param view_name: name of the view
        :params fields: fields to including in response data
        """
        self._require_auth()
        if not fields:
            fields = self.fields
        # Encoding for special character in view name
        encoded_view_name = quote(f"{view_name}".encode('utf-8'))
        query_params_str = f"fields={fields}&filter=name:eq('{encoded_view_name}')"
        response = self.v2_client.http_get(
            f"/configurations/{configuration_id}/views?{query_params_str}")
        if response.get('count') == 0 or len(response.get('data', [])) <= 0 or not response.get('data')[0].get('id'):
            raise ClientError("View named {} not found".format(view_name))
        return response

    def get_zones_by_hint(self, ancestor_id, hint='', limit=10, fields=''):
        """
        GET zones start with hint in configuration
        :param ancestor_id: ancestor id which contains the zones searched
        :param hint: hint which zones start with
        :param limit: number of result
        :param fields: fields to including in response data
        """
        self._require_auth()
        if not fields:
            fields = self.fields + ', absoluteName, view'
        encoded_hint = quote(f"{hint}".encode('utf-8'))
        query_params_str = f"fields={fields}&filter=ancestor.id:{ancestor_id} " \
                           f"and absoluteName:startsWith('{encoded_hint}') " \
                           f"and type:ne('ExternalHostsZone')&limit={limit}&total=true"
        zones = self.v2_client.http_get(f"/zones/?{query_params_str}",
                                        expected_status_codes=self.expected_status_code)
        for zone in zones['data']:
            if zone.get('view'):
                zone['view'] = zone.get('view').get('name')
        if zones.get('_links'):
            zones.pop('_links')
        return zones

    def get_servers_by_hint(self, ancestor_id, hint='', limit=10, fields=''):
        """
        GET servers by hint in an ancestor_id
        :param ancestor_id: ancestor id which contains the servers
        :param hint: hint which servers start with
        :param limit: number of result
        :param fields: fields including in response data
        """
        self._require_auth()
        if not fields:
            fields = self.fields
        encoded_hint = quote(f"{hint}".encode('utf-8'))
        query_params_str = f"fields={fields}&filter=ancestor.id:{ancestor_id} and name:startsWith('{encoded_hint}')&limit={limit}&total=true"
        response = self.v2_client.http_get(f"/servers?{query_params_str}",
                                           expected_status_codes=self.expected_status_code)
        return response

    def get_interfaces_by_hint(self, ancestor_id, hint='', limit=10, fields=''):
        """
        GET interface start with hint in an ancestor_id
        :param ancestor_id: ancestor id which contains the interface searched
        :param hint: hint which interfaces start with
        :param limit: number of result
        :param fields: fields to including in response data
        """
        self._require_auth()
        if not fields:
            fields = self.fields + ', server'
        encoded_hint = quote(f"{hint}".encode('utf-8'))
        query_params_str = f"fields={fields}&filter=ancestor.id:{ancestor_id} and name:startsWith('{encoded_hint}')&limit={limit}&total=true"
        response = self.v2_client.http_get(f"/interfaces/?{query_params_str}",
                                           expected_status_codes=self.expected_status_code)
        return response

    def get_interfaces_by_server(self, server_id, fields=None):
        """
        GET a collection of all configured server interfaces of a server.
        :param server_id: id of server
        :param fields: fields to including in response data
        """
        self._require_auth()
        if fields is None:
            fields = self.fields + ', server'
        response = self.v2_client.http_get(f"/servers/{server_id}/interfaces/?fields={fields}",
                                           expected_status_codes=self.expected_status_code)
        return response

    def get_networks_and_blocks_by_ipv4_and_ipv6_hint(self, ancestor_id, ipv4_hint='', ipv6_hint='', raw_hint='',
                                                      limit=10, fields=''):
        """
        GET interface start with hint in an ancestor_id
        :param ancestor_id: ancestor id which contains the networks and blocks
        :param ipv4_hint: reverse  ipv4 hint which networks or blocks range starts with
        :param ipv6_hint: reverse ipv6 hint which networks or blocks range starts with
        :param raw_hint: optional hint to revalidate the data after getting API data
        :param limit: number of result
        :param fields: fields to including in response data
        """
        try:
            self._require_auth()
            if not fields:
                fields = self.fields + ', range'
            query_params_str = f"fields={fields}&limit={limit}&total=true&filter=ancestor.id:{ancestor_id}"
            if ipv6_hint:
                query_params_str += f" and range:startsWith('{ipv6_hint.replace('x', '')}')"
            if ipv4_hint:
                if ipv6_hint:
                    query_params_str += f' or ancestor.id:{ancestor_id} and '
                else:
                    query_params_str += ' and '
                query_params_str += f"range:startsWith('{ipv4_hint}')"
            blocks = self.v2_client.http_get(f"/blocks?{query_params_str}",
                                             expected_status_codes=self.expected_status_code)
            networks = self.v2_client.http_get(f"/networks?{query_params_str}",
                                               expected_status_codes=self.expected_status_code)
            for network in networks.get('data'):
                network['reverseZoneName'] = common.get_reverse_zone_name(network.get('range'))
            for block in blocks.get('data'):
                block['reverseZoneName'] = common.get_reverse_zone_name(block.get('range'))
            blocks_and_networks_data = {
                'count': networks.get('count', 0) + blocks.get('count', 0),
                'totalCount': networks.get('totalCount', 0) + blocks.get('totalCount', 0),
                'data': networks.get('data', [0]) + blocks.get('data', [])
            }

            blocks_and_networks_data['data'] = list(
                filter(lambda x: raw_hint in x['reverseZoneName'],
                       blocks_and_networks_data['data']))
            blocks_and_networks_data['count'] = len(blocks_and_networks_data['data'])
            blocks_and_networks_data['totalCount'] = blocks_and_networks_data['count']
            if blocks_and_networks_data['count'] > limit:
                blocks_and_networks_data['count'] = limit
                blocks_and_networks_data['data'] = blocks_and_networks_data['data'][:limit]
            return blocks_and_networks_data
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return {
                'count': 0,
                'data': [],
                'totalCount': 0
            }

    def get_zones_with_view_name(self, zones):
        for zone in zones:
            view_id = get_view_of_zone(self, zone)
            zone['view'] = self.get_view_by_id(view_id).get('name', '') if view_id != 0 else ''
            zone.pop('_links')
        return

    def get_servers_in_server_group(self, server_group_id, filters='', fields=''):
        if not fields:
            fields = self.fields + ", _links"
        query_string = '?fields={}'.format(fields)
        if filters:
            query_string += "&filter={}".format(filters)
        self._require_auth()
        response = self.v2_client.http_get(
            "/serverGroups/{}/servers".format(server_group_id) + query_string,
            expected_status_codes=self.expected_status_code)
        return response
