import random

from flask import json
from flask_restful import Resource
from virtual_api.api_handler import entity_by_name_users, views_file, \
    get_pools_under_id, servers_file, network_interfaces_file, deployment_roles_file, get_object_by_entityid, \
    get_entity_by_id, client_options_file, get_ip_address, json_response, read_file, get_view, bluecat_api_list, \
    system_info, ip_address_file
from webargs import fields
from webargs.flaskparser import use_args


class session(Resource):

    def get(self):
        return json_response(read_file(bluecat_api_list))


class get_system_info(Resource):

    def get(self):
        return json_response(system_info)


class get_entity_by_name(Resource):
    parameters = {"name": fields.Str(required=True),
                  "type": fields.Str(required=True),
                  "parentId": fields.Int(required=True)}

    @use_args(parameters)
    def get(self, args):
        type = args['type']
        if type == 'User':
            return entity_by_name_users
        if type == 'Configuration':
            name = args['name']
            return get_view(name)
        if type == 'View':
            return {
                "id": 0,
                "name": None,
                "type": None,
                "properties": None
            }


class login(Resource):
    parameters = {"username": fields.Str(missing="username param is missing"),
                  "password": fields.Str(missing="password param is missing")}

    @use_args(parameters)
    def get(self, args):
        username = args['username']
        if str(username).__contains__('missing'):
            return json_response(username, 400)

        password = args['password']
        if str(password).__contains__('missing'):
            return json_response(password, 400)

        if username == 'gateway-user' and password == 'admin':
            return json_response(
                "Session Token-> BAMAuthToken: r0JiHMTU0NTkyNjAxOTM3MDpucXVvY3RoYWk= <- for User : gateway-user")
        else:
            return json_response('Invalid username or password.', 401)


class get_entities(Resource):
    parameters = {"count": fields.Int(required=True),
                  "start": fields.Int(required=True),
                  "type": fields.Str(required=True),
                  "parentId": fields.Int(required=True)}

    @use_args(parameters)
    def get(self, args):
        type = args['type']
        parent_id = args['parentId']
        if type == 'Configuration':
            start = args['start']
            count = args['count']
            list = json.loads(read_file(views_file))
            return list[start:(start + count)]
        if type == 'IP4Block':
            return get_pools_under_id(parent_id, type)
        if type == 'IP4Network':
            return get_pools_under_id(parent_id, type)
        if type == 'IP6Block':
            return get_pools_under_id(parent_id, type)
        if type == 'IP6Network':
            return get_pools_under_id(parent_id, type)
        if type == 'Server':
            return json.loads(read_file(servers_file))
        if type == 'NetworkServerInterface':
            return json.loads(read_file(network_interfaces_file))
        if type == 'PublishedServerInterface':
            return []
        if type == 'IP4Address':
            return json.loads(read_file(ip_address_file))


class deployment_roles(Resource):
    parameters = {"entityId": fields.Int(required=True)}

    @use_args(parameters)
    def get(self, args):
        entity_id = args['entityId']
        return get_object_by_entityid(deployment_roles_file, entity_id)


class entity_by_id(Resource):
    parameters = {"id": fields.Int(required=True)}

    @use_args(parameters)
    def get(self, args):
        id = args['id']
        return get_entity_by_id(id)


class deployment_options(Resource):
    parameters = {"optionTypes": fields.Str(required=True),
                  "entityId": fields.Int(required=True),
                  "serverId": fields.Int(required=True)}

    @use_args(parameters)
    def get(self, args):
        entity_id = args['entityId']
        return get_object_by_entityid(client_options_file, entity_id)


class add_entity(Resource):
    parameters = {"parentId": fields.Int(required=True)}

    @use_args(parameters)
    def post(self, args):
        return json_response("{:0>6d}".format(random.randint(1, 9999999), 6))


class add_ip4_block_by_cidr(Resource):
    parameters = {"CIDR": fields.Str(required=True),
                  "properties": fields.Str(required=True),
                  "parentId": fields.Int(required=True)}

    @use_args(parameters)
    def post(self, args):
        return json_response("{:0>6d}".format(random.randint(1, 9999999), 6))


class add_ip6_block_by_prefix(Resource):
    parameters = {"prefix": fields.Str(required=True),
                  "properties": fields.Str(required=True),
                  "parentId": fields.Int(required=True)}

    @use_args(parameters)
    def post(self, args):
        return json_response("{:0>6d}".format(random.randint(1, 9999999), 6))


class add_dhcp_deployment_role(Resource):
    parameters = {"type": fields.Str(required=True),
                  "properties": fields.Str(required=True),
                  "entityId": fields.Int(required=True),
                  "serverInterfaceId": fields.Int(required=True)}

    @use_args(parameters)
    def post(self, args):
        return json_response("{:0>6d}".format(random.randint(1, 9999999), 6))


class add_dns_deployment_role(Resource):
    parameters = {"type": fields.Str(required=True),
                  "properties": fields.Str(required=True),
                  "entityId": fields.Int(required=True),
                  "serverInterfaceId": fields.Int(required=True)}

    @use_args(parameters)
    def post(self, args):
        return json_response("{:0>6d}".format(random.randint(1, 9999999), 6))


class add_view(Resource):
    parameters = {"configurationId": fields.Int(required=True),
                  "properties": fields.Str(required=True),
                  "name": fields.Str(required=True)}

    @use_args(parameters)
    def post(self, args):
        return json_response("{:0>6d}".format(random.randint(1, 9999999), 6))


class add_dhcp_client_deployment_option(Resource):
    parameters = {"entityId": fields.Int(required=True),
                  "name": fields.Str(required=True),
                  "value": fields.Str(required=True),
                  "properties": fields.Str(required=True)}

    @use_args(parameters)
    def post(self, args):
        name = args['name']
        if str(name).__contains__('wrong'):
            return json_response('option is wrong', 400)
        return json_response("{:0>6d}".format(random.randint(1, 9999999), 6))


class add_dhcp6_client_deployment_option(Resource):
    parameters = {"entityId": fields.Int(required=True),
                  "name": fields.Str(required=True),
                  "value": fields.Str(required=True),
                  "properties": fields.Str(required=True)}

    @use_args(parameters)
    def post(self, args):
        name = args['name']
        if str(name).__contains__('wrong'):
            return json_response('option is wrong', 400)
        return json_response("{:0>6d}".format(random.randint(1, 9999999), 6))


class delete(Resource):
    parameters = {"objectId": fields.Int(required=True)}

    @use_args(parameters)
    def delete(self, args):
        return json_response('')


class add_ip4_network(Resource):
    parameters = {"CIDR": fields.Str(required=True),
                  "properties": fields.Str(required=True),
                  "blockId": fields.Int(required=True)}

    @use_args(parameters)
    def post(self, args):
        return json_response("{:0>6d}".format(random.randint(1, 9999999), 6))


class add_ip6_network(Resource):
    parameters = {"prefix": fields.Str(required=True),
                  "properties": fields.Str(required=True),
                  "name": fields.Str(required=True),
                  "parentId": fields.Int(required=True)}

    @use_args(parameters)
    def post(self, args):
        return json_response("{:0>6d}".format(random.randint(1, 9999999), 6))


class add_ip6_address(Resource):
    parameters = {"type": fields.Str(required=True),
                  "properties": fields.Str(required=True),
                  "name": fields.Str(required=True),
                  "containerId": fields.Int(required=True)}

    @use_args(parameters)
    def post(self, args):
        return json_response("{:0>6d}".format(random.randint(1, 9999999), 6))


class get_ip4_address(Resource):
    parameters = {"containerId": fields.Int(required=True),
                  "address": fields.Str(required=True)}

    @use_args(parameters)
    def get(self, args):
        address = args['address']
        return get_ip_address(address)


class get_ip6_address(Resource):
    parameters = {"containerId": fields.Int(required=True),
                  "address": fields.Str(required=True)}

    @use_args(parameters)
    def get(self, args):
        address = args['address']
        return get_ip_address(address)


class assign_ip4_address(Resource):
    parameters = {"macAddress": fields.Str(required=True),
                  "hostInfo": fields.Str(required=True),
                  "configurationId": fields.Int(required=True),
                  "ip4Address": fields.Str(required=True),
                  "action": fields.Str(required=True),
                  "properties": fields.Str(required=True)}

    @use_args(parameters)
    def post(self, args):
        return json_response('')
