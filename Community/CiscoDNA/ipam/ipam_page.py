# Copyright 2018 BlueCat Networks. All rights reserved.
# -*- coding: utf-8 -*-
import urllib

import config.default_config as config
# auto-login
from app_user import UserSession
from bluecat import route, util
from bluecat.api_exception import AuthenticationError, PortalException, APIException
from bluecat.constants import MAX_COUNT
from bluecat.entity import Entity
from bluecat.util import properties_to_map, map_to_properties
from flask import request, g, jsonify, Response, flash
from main_app import app
from netaddr import IPNetwork

from .ipam_exception import IpPoolBadRequestException, IpPoolAlreadyExistsException, \
    IpPoolInUseException, IpSubpoolNotEmptyException, IpSubpoolAlreadyExistsException, IpAddressNotAvailableException


@app.before_request
def my_before_request():
    token = request.headers.get('auth')
    if token is not None:
        u = get_user_from_session(token)
        g.user = u
        g.use_rest = True
        if u:
            g.user.logger.debug(request)


@route(app, '/ipam/token', methods=['POST'])
def get_token():
    """get token to authenticate"""
    try:
        args = request.get_json()
        username = args['username']
        password = args['password']
        bam_url = config.api_url[0][1]

        u = UserSession.validate(bam_url, username, password)

        if u is None:
            raise AuthenticationError(
                'Invalid username or password.',
                status_code=401,
                payload={'WWW-Authenticate': 'Basic realm="Login Required"'})

        u.logger.debug(args)
        token = u.get_unique_name()
        return jsonify({"tokenkey": 'auth',
                        "tokenvalue": token})
    except AuthenticationError as au_err:
        return Response(au_err.description, status=au_err.code)
    except PortalException as con_err:
        return Response(con_err.__str__(), status=408)
    except Exception as ex:
        return Response(ex.__str__(), status=400)


@route(app, '/ipam/pool', methods=['POST'])
def create_pool():
    """
    Payload request = {
        "view":"DNACenter",
        "poolName":"DNACPool",
        "poolCidr":"10.0.0.0/8",
        "DHCPServerip":[],
        "DNSServerip":[],
        "ClientOptions":[{"key":"option43", "keyValue":"172.0.0.1"}]
    }
    :return: None
    """
    args = request.get_json()
    g.user.logger.debug(args)
    new_entity_id = None
    # create pool
    try:
        message_check = validate_require_param(args, {'view': False, 'poolName': False, 'poolCidr': True})
        if len(message_check) > 0:
            err_message = convert_message_to_string(message_check)
            return Response(err_message, status=400)

        # get parameters
        pool_name = args['poolName']
        pool_cidr = args['poolCidr']
        config_name = args['view']

        config_id = create_configuration(config_name)

        subpool = get_child_ip(config_id, pool_cidr)
        if subpool is not None:
            if subpool == pool_cidr:
                raise IpPoolAlreadyExistsException('A pool \'{0}\' already exists'.format(pool_cidr))
            else:
                raise IpPoolInUseException(
                    'A parent pool \'{0}\' has child pool \'{1}\''.format(pool_cidr, subpool))

        ip = pool_cidr.split('/')[0]
        if util.is_valid_ipv4_address(ip):
            new_entity_id = create_ipv4_block(config_id, pool_cidr, pool_name)
        if util.is_valid_ipv6_address(ip):
            new_entity_id = create_ipv6_block(config_id, pool_cidr, pool_name)

    except IpPoolInUseException as inus_err:
        return Response(inus_err.description, status=405)
    except IpPoolAlreadyExistsException as exist_err:
        return Response(exist_err.description, status=405)
    except Exception as ex:
        return Response(ex.__str__(), status=400)

    keys = args.keys()
    options_message = []

    if new_entity_id is not None and 'DHCPServerip' in keys:
        dhcp_server = args['DHCPServerip']
        interfaces = get_server_interface_id(config_id)
        options_message += add_dhcp_servers(config_name, new_entity_id, dhcp_server, interfaces)

    if new_entity_id is not None and 'DNSServerip' in keys:
        dns_servers = args['DNSServerip']
        dns_view_name = config_name + '_view'
        interfaces = get_server_interface_id(config_id)
        options_message += add_dns_servers(config_id, config_name, new_entity_id, dns_servers, interfaces,
                                           dns_view_name)

    if new_entity_id is not None and 'ClientOptions' in keys:
        client_options = args['ClientOptions']
        is_ipv4 = True
        ip = pool_cidr.split('/')[0]
        if util.is_valid_ipv6_address(ip):
            is_ipv4 = False
        options_message += add_client_options(client_options, new_entity_id, is_ipv4)

    if len(options_message) > 0:
        return Response(convert_message_to_string(options_message), status=200)

    return Response(status=200)


@route(app, '/ipam/subpool', methods=['POST'])
def create_subpool():
    """
    Payload request = {
        "view":"DNACenter",
        "subpoolName":"SanJosePool",
        "poolCidr":"10.0.0.0/16",
        "gatewayip":"10.0.0.1",
        "DHCPServerip":[],
        "DNSServerip":[],
        "ClientOptions":[{"key":"option43", "keyValue":"172.0.0.1"}]
    }
    :return: None
    """
    args = request.get_json()
    g.user.logger.debug(args)
    new_entity_id = None
    # create pool
    try:
        # get parameters
        message_check = validate_require_param(args, {'view': False, 'subpoolName': False, 'poolCidr': True})
        if len(message_check) > 0:
            err_message = convert_message_to_string(message_check)
            return Response(err_message, status=400)

        pool_cidr = args['poolCidr']
        subpool_name = args['subpoolName']
        config_name = args['view']

        config_id = create_configuration(config_name)

        subpool = get_child_ip(config_id, pool_cidr)
        if subpool is not None:
            if subpool == pool_cidr:
                raise IpSubpoolAlreadyExistsException('A pool \'{0}\' already exists'.format(pool_cidr))
            else:
                raise IpSubpoolNotEmptyException(
                    'A parent pool \'{0}\' has child pool \'{1}\''.format(pool_cidr, subpool))

        ip = pool_cidr.split('/')[0]
        if util.is_valid_ipv4_address(ip):
            if 'gatewayip' in args.keys():
                new_entity_id = create_ipv4_network(config_id, pool_cidr, subpool_name, args['gatewayip'])
            else:
                new_entity_id = create_ipv4_network(config_id, pool_cidr, subpool_name)
                gateway_id = get_gateway_under_network(new_entity_id)
                if gateway_id is not None:
                    g.user.get_api()._api_client.service.delete(gateway_id)

        elif util.is_valid_ipv6_address(ip):
            new_entity_id = create_ipv6_network(config_id, pool_cidr, subpool_name)
            if 'gatewayip' in args.keys():
                addip6_gateway(new_entity_id, args['gatewayip'])

    except IpSubpoolNotEmptyException as not_empty_err:
        return Response(not_empty_err.description, status=405)
    except IpSubpoolAlreadyExistsException as exist_err:
        return Response(exist_err.description, status=405)
    except Exception as ex:
        return Response(ex.__str__(), status=400)

    keys = args.keys()
    options_message = []
    if new_entity_id is not None and 'DHCPServerip' in keys:
        dhcp_server = args['DHCPServerip']
        interfaces = get_server_interface_id(config_id)
        options_message += add_dhcp_servers(config_name, new_entity_id, dhcp_server, interfaces)

    if new_entity_id is not None and 'DNSServerip' in keys:
        dns_servers = args['DNSServerip']
        dns_view_name = config_name + '_view'
        interfaces = get_server_interface_id(config_id)
        options_message += add_dns_servers(config_id, config_name, new_entity_id, dns_servers, interfaces,
                                           dns_view_name)

    if new_entity_id is not None and 'ClientOptions' in keys:
        client_options = args['ClientOptions']
        is_ipv4 = True
        ip = pool_cidr.split('/')[0]
        if util.is_valid_ipv6_address(ip):
            is_ipv4 = False
        options_message += add_client_options(client_options, new_entity_id, is_ipv4)

    if len(options_message) > 0:
        return Response(convert_message_to_string(options_message), status=200)

    return Response(status=200)


@route(app, '/ipam/view')
def get_views():
    """
    url: http://localhost:5000/ipam/view?limit=10&offset=2
    :return:
    """
    try:
        if g.user is None:
            raise AuthenticationError('Authentication is failed')

        limit = 500
        offset = 0

        keys = request.args.keys()
        g.user.logger.debug(request.args)
        if 'limit' in keys:
            limit = int(request.args.get('limit'))
        if 'offset' in keys:
            offset = int(request.args.get('offset')) - 1

        if limit < 0:
            limit = 500

        if offset < 0:
            offset = 0

        configs = g.user.get_api()._api_client.service.getEntities(0, Entity.Configuration, offset, limit)
        views = []
        for c in configs:
            views.append({'view': c['name']})
        return jsonify(views)
    except AuthenticationError as au_err:
        return Response(au_err.description, status=au_err.code)
    except PortalException as con_err:
        return Response(con_err.__str__(), status=408)
    except Exception as ex:
        return Response(ex.__str__(), status=400)


@route(app, '/ipam/ippool/<string:view>')
def get_pools(view):
    """get all pool under configuration (view)"""
    config = g.user.get_api()._api_client.service.getEntityByName(0, view, Entity.Configuration)
    if config['name'] is None:
        return jsonify([])

    parent_id = config['id']
    res = []
    if not 'ippoolcidr' in request.args.keys():
        return jsonify([])
    try:
        cidr = request.args.get('ippoolcidr')
        pools = get_empty_pools_under_cidr(parent_id, cidr)
        for pool in pools:
            obj = {}
            obj['view'] = view
            obj['ipPoolCidr'] = get_ip_cidr(pool)
            obj['ipPoolName'] = get_pool_name(pool)
            obj['gatewayIp'] = get_gateway(pool)
            obj['dhcpServer'] = get_deploy_role_server(pool, 'DHCP')
            obj['dnsServer'] = get_deploy_role_server(pool, 'DNS')
            obj['ClientOptions'] = get_client_options(pool)
            res.append(obj)
    except Exception as ex:
        g.user.logger.debug(ex.__str__())
        return jsonify([])
    return jsonify(res)


@route(app, '/ipam/pool/<string:view>/<string:poolcidr>', methods=['DELETE'])
def release_pool(view, poolcidr):
    """release pool under configuration (view)"""
    try:
        config = g.user.get_api()._api_client.service.getEntityByName(0, view, Entity.Configuration)
        if config['type'] is None:
            raise IpPoolBadRequestException('View \'{0}\' does not exist'.format(view))
        config_id = config['id']

        poolcidr = urllib.parse.unquote(poolcidr)
        pool = find_obj_by_cidr(get_pools_under_id(config_id), poolcidr)
        if pool is None:
            raise IpPoolBadRequestException('Pool \'{0}\' does not exist'.format(poolcidr))
        g.user.get_api()._api_client.service.delete(pool['id'])

        return Response(status=200)
    except IpPoolBadRequestException as ex:
        return Response(ex.description, status=400)


def create_configuration(name):
    """if configuration is exist then return id, if not exist then create configuration"""
    config = g.user.get_api()._api_client.service.getEntities(0, Entity.Configuration, 0, MAX_COUNT)
    for c in config:
        if c['name'] == name:
            return c['id']
    config = {}
    config['type'] = 'Configuration'
    config['name'] = name
    config['id'] = None
    return g.user.get_api()._api_client.service.addEntity(0, config)


def has_child(new_ip, ip):
    """check ip is child of new_ip"""
    try:
        return IPNetwork(ip) in IPNetwork(new_ip)
    except:
        return False


def get_child_ip(config_id, new_ip):
    """get child of new_ip under configuration"""
    current_child = None
    list_pool = get_pools_under_id(config_id)
    for parent in list_pool:
        cidr = get_ip_cidr(parent)
        if new_ip == cidr:
            return cidr

        if has_child(new_ip, cidr):
            temp_child = cidr
            if has_child(temp_child, current_child):
                current_child = temp_child
            else:
                current_child = cidr
    return current_child


def get_parent(config_id, new_ip):
    """get parent of new_ip under configutation"""
    list_pool = get_pools_under_id(config_id)
    for pool in list_pool:
        cidr = get_ip_cidr(pool)
        if has_child(cidr, new_ip):
            return pool
    return None


def create_ipv4_block(config_id, pool_cidr, pool_name):
    """create ipv4 block under configuration"""
    properties = "name=" + pool_name
    return g.user.get_api()._api_client.service.addIP4BlockByCIDR(config_id, pool_cidr, properties)


def create_ipv4_network(config_id, pool_cidr, pool_name, gateway=None):
    """create ipv4 network under configuration"""
    properties = "name=" + pool_name
    if gateway is not None:
        properties += "|gateway=" + gateway
    parent = get_parent(config_id, pool_cidr)
    parent_id = config_id
    if parent is not None:
        parent_id = parent['id']
    return g.user.get_api()._api_client.service.addIP4Network(parent_id, pool_cidr, properties)


def create_ipv6_block(config_id, pool_cidr, pool_name):
    """create ipv6 block under configuration"""
    return g.user.get_api()._api_client.service.addIP6BlockByPrefix(config_id, pool_cidr, pool_name, '')


def create_ipv6_network(config_id, pool_cidr, pool_name):
    """create ipv6 network under configuration"""
    parent = get_parent(config_id, pool_cidr)
    parent_id = config_id
    if parent is not None:
        parent_id = parent['id']
    return g.user.get_api()._api_client.service.addIP6NetworkByPrefix(parent_id, pool_cidr, pool_name, '')


def addip6_gateway(parent_id, gateway_ip, type='IP6Address', properties='state=GATEWAY'):
    """add ipv6 gateway for ipv6 address"""
    g.user.get_api()._api_client.service.addIP6Address(parent_id, gateway_ip, type, '', properties)


def get_pools_under_id(id):
    """get all pool under entity id"""
    list_pool = []
    types = [Entity.IP4Block, Entity.IP4Network, Entity.IP6Block, Entity.IP6Network]
    for type in types:
        pools = get_pool_by_type(id, type)
        list_pool = pools.__add__(list_pool)

    for pool in list_pool:
        id = pool['id']
        pools = get_pools_under_id(id)
        list_pool = pools.__add__(list_pool)
    return list_pool


def get_empty_pools_under_cidr(id, cidr=None):
    """get the empty block pool under entity id"""
    container = ['IP4Block', 'IP6Block']
    empty_pools = []
    pools = get_pools_under_id(id)
    for pool in pools:
        type = pool['type']
        if is_leaves(pool) and type in container:
            if cidr is None:
                empty_pools.append(pool)
            elif has_child(cidr, get_ip_cidr(pool)):
                empty_pools.append(pool)

    return empty_pools


def find_obj_by_cidr(list_pool, ip_pool_cidr):
    """find pool by cidr in list"""
    for pool in list_pool:
        cidr = get_ip_cidr(pool)
        if cidr == ip_pool_cidr:
            return pool
    return None


def get_pool_by_type(parent_id, type):
    """get list pool by type under entity id"""
    try:
        return g.user.get_api()._api_client.service.getEntities(parent_id, type, 0, MAX_COUNT)
    except:
        return []


def get_pool_name(obj):
    """get name of pool"""
    name = obj['name']
    if name is None:
        return ''
    return name


def get_ip_cidr(obj):
    """get cidr of pool"""
    properties = properties_to_map(obj['properties'])
    type = obj['type']
    if 'IP4Block' == type or 'IP4Network' == type:
        return properties['CIDR']
    else:
        return properties['prefix']


def get_user_from_session(access_token):
    """ Checks if BAM connection is still active.
    If the API connection has been lost, the user is treated as logged out.
    """
    u = UserSession.from_username(access_token)
    if u:
        try:
            u.get_api().get_configurations()
        except APIException as e:
            if any(message in e.get_message() for message in ['UNAUTHORIZED',
                                                              'You are not logged on',
                                                              'Not logged in']):
                u.logout()
                u = None
        except Exception as e:
            flash('Error connecting to the BAM! Please check the user session log for more information!')
            u.logger.critical('Connection error occurred! EXCEPTION: %s' % e.message)
            u = None
        except StopIteration:
            pass
    return u


def is_leaves(pool):
    """check pool is leaves"""
    list_pool = []
    id = pool['id']
    types = [Entity.IP4Block, Entity.IP4Network, Entity.IP6Block, Entity.IP6Network]
    for type in types:
        pools = get_pool_by_type(id, type)
        list_pool = pools.__add__(list_pool)
    return len(list_pool) == 0


def assign_gateway(parent_id, gateway_ip):
    """assign gateway for entity"""
    options_message = []
    try:
        ip = gateway_ip.split('/')[0]
        if util.is_valid_ipv4_address(ip):
            entity = g.user.get_api()._api_client.service.getEntityById(parent_id)
            properties = properties_to_map(entity['properties'])
            properties['gateway'] = gateway_ip
            entity['properties'] = map_to_properties(properties)
            g.user.get_api()._api_client.service.update(entity)
        elif util.is_valid_ipv6_address(ip):
            addip6_gateway(parent_id, gateway_ip)
        else:
            options_message.append('Gateway Ip \'{0}\' is invalid'.format(gateway_ip))
            return options_message
    except Exception as ex:
        options_message.append('Assign gateway \'{0}\' is failed, exception: {1}'.format(gateway_ip, ex.message))
    return options_message


def add_dhcp_servers(config_name, parent_id, dhcp_input, interfaces):
    """add dhcp server for entity"""
    options_message = []
    for server in dhcp_input:
        count = 0
        for face in interfaces:
            if server == face['ipaddress']:
                count += 1
        if count == 0:
            options_message.append(
                'Note: DHCP Server \'{0}\' is not exist under view \'{1}\''.format(server, config_name))
    is_first = True
    for server in dhcp_input:
        for face in interfaces:
            if server == face['ipaddress']:
                try:
                    if is_first:
                        g.user.get_api()._api_client.service.addDHCPDeploymentRole(parent_id, face['id'], 'MASTER', '')
                        is_first = False
                    else:
                        g.user.get_api()._api_client.service.addDHCPDeploymentRole(parent_id, face['id'], 'NONE', '')
                except Exception as ex:
                    options_message.append(
                        'Note: add DNS server \'{0}\' is failed, exception: {1}'.format(server, ex.message))
    return options_message


def add_dns_servers(config_id, config_name, parent_id, dns, interfaces, dns_view='default'):
    """add dns server for entity"""
    options_message = []
    try:
        dns_view_id = create_dns_view(config_id, dns_view)
        properties = 'view=' + str(dns_view_id)
    except Exception as ex:
        options_message.append('Add \'{0}\' DNS view is failed, exception: {1}'.format(dns_view, ex.message))
    for server in dns:
        count = 0
        for face in interfaces:
            if server == face['ipaddress']:
                count += 1
        if count == 0:
            options_message.append(
                'Note: DNS Server \'{0}\' is not exist under view \'{1}\''.format(server, config_name))

    is_first = True
    for server in dns:
        for face in interfaces:
            if server == face['ipaddress']:
                try:
                    if is_first:
                        g.user.get_api()._api_client.service.addDNSDeploymentRole(parent_id, face['id'], 'MASTER',
                                                                                  properties)
                        is_first = False
                    else:
                        g.user.get_api()._api_client.service.addDNSDeploymentRole(parent_id, face['id'], 'NONE',
                                                                                  properties)
                except Exception as ex:
                    options_message.append(
                        'Note: add DNS server \'{0}\' is failed, exception: {1}'.format(server, ex.message))
    return options_message


def add_client_options(client_options, new_entity_id, is_ipv4=True):
    """add client options for entity"""
    options_message = []
    for option in client_options:
        message = validate_require_param(option, {'key': False, 'keyValue': False})
        if len(message) > 0:
            options_message.append(convert_message_to_string(message))
        else:
            keyname = option['key']
            keyvalue = option['keyValue']
            try:
                if is_ipv4:
                    g.user.get_api()._api_client.service.addDHCPClientDeploymentOption(new_entity_id, keyname, keyvalue,
                                                                                       '')
                else:
                    g.user.get_api()._api_client.service.addDHCP6ClientDeploymentOption(new_entity_id, keyname,
                                                                                        keyvalue, '')
            except Exception as ex:
                options_message.append(
                    'Note: add client option \'{0}\' is failed, exception: {1}'.format(option, ex.message))

    return options_message


def get_server_interface_id(config_id):
    """get server interface under configuration"""
    interfaces = []
    servers = g.user.get_api()._api_client.service.getEntities(config_id, Entity.Server, 0, MAX_COUNT)
    for server in servers:
        face = g.user.get_api()._api_client.service.getEntities(server['id'], Entity.NetworkServerInterface, 0,
                                                                MAX_COUNT)
        interfaces += face
        face = g.user.get_api()._api_client.service.getEntities(server['id'], Entity.PublishedServerInterface, 0,
                                                                MAX_COUNT)
        interfaces += face
    list_face = []
    for face in interfaces:
        type = face['type']
        id = face['id']
        properties = properties_to_map(face['properties'])
        ipaddress = ''
        if 'NetworkServerInterface' == type:
            ipaddress = properties['defaultInterfaceAddress']
        if 'PublishedServerInterface' == type:
            ipaddress = properties['publishedInterfaceAddress']

        list_face.append({
            'type': type,
            'id': id,
            'ipaddress': ipaddress
        })

    return list_face


def create_dns_view(config_id, view_name):
    """create dns view under configuration if not exist"""
    view = g.user.get_api()._api_client.service.getEntityByName(config_id, view_name, Entity.View)
    if view['name'] is None:
        return g.user.get_api()._api_client.service.addView(config_id, view_name, '')
    return view['id']


def validate_require_param(args, list_param):
    """validate parameter is required"""
    message = []
    keys = args.keys()
    for param in list_param.keys():
        if not param in keys:
            message.append('Parameter \'{0}\' is required'.format(param))
        else:
            if '' == str(args[param]).strip():
                message.append('Parameter \'{0}\' is not empty'.format(param))
            else:
                if list_param[param]:
                    s = validate_ip(args[param])
                    if '' != s:
                        message.append(s)
    return message


def validate_ip(pool_cidr):
    message = ''
    ip = pool_cidr.split('/')[0]
    if util.is_valid_ipv4_address(ip):
        pass
    elif util.is_valid_ipv6_address(ip):
        pass
    else:
        message = 'Pool \'{0}\' is invalid'.format(pool_cidr)
    return message


def convert_message_to_string(message):
    s = ''
    for ex in message:
        s += ex + '\n'
    return s


def get_gateway(obj):
    """get gateway of pool"""
    properties = properties_to_map(obj['properties'])
    if 'gateway' in properties.keys():
        return properties['gateway']
    else:
        return ''


def get_client_options(obj):
    """get client options of pool"""
    try:
        list_option = []
        options = g.user.get_api()._api_client.service.getDeploymentOptions(obj['id'], '', 0)
        for op in options:
            key = op['name']
            keyvalue = op['value']
            list_option.append({key: keyvalue})

        return list_option
    except:
        return []


def get_deploy_role_server(obj, type):
    """get deployment role server of pool by type (DHCP, DNS)"""
    list_server = []
    try:
        id = obj['id']
        servers = g.user.get_api()._api_client.service.getDeploymentRoles(id)
        for server in servers:
            if server['service'] == type:
                interface_id = server['serverInterfaceId']
                obj_interface = g.user.get_api()._api_client.service.getEntityById(interface_id)
                properties = properties_to_map(obj_interface['properties'])
                if 'defaultInterfaceAddress' in properties.keys():
                    list_server.append(properties['defaultInterfaceAddress'])
    except:
        return []
    return list_server


@route(app, '/ipam/assignip', methods=['POST'])
def assign_ip():
    """assign ip in list input"""
    try:
        args = request.get_json()
        g.user.logger.debug(args)
        message_check = validate_require_param(args, {'view': False, 'iplist': False})
        if len(message_check) > 0:
            err_message = convert_message_to_string(message_check)
            return Response(err_message, status=400)

        view = args['view']
        ip_list = args['iplist']

        config = g.user.get_api()._api_client.service.getEntityByName(0, view, Entity.Configuration)
        if config['type'] is None:
            raise Exception('View \'{0}\' does not exist'.format(view))
        config_id = config['id']

        # MAKE_RESERVED, MAKE_STATIC
        for ip in ip_list:
            if is_assigned(config_id, ip):
                raise IpAddressNotAvailableException('{0} is not available'.format(ip))
            g.user.get_api()._api_client.service.assignIP4Address(config_id, ip, '', '', 'MAKE_RESERVED', '')

        return Response(status=200)
    except IpAddressNotAvailableException as avai_err:
        return Response(avai_err.description, status=405)
    except Exception as ex:
        return Response(ex.__str__(), status=400)


def is_assigned(config_id, ip_address):
    """check ip address under configuration is assigned or not"""
    obj = g.user.get_api()._api_client.service.getIP4Address(config_id, ip_address)
    if obj['properties'] is None:
        return False
    return True


@route(app, '/ipam/releaseip/<string:view>', methods=['DELETE'])
def release_ip(view):
    """release ip in list input"""
    try:
        args = request.args
        g.user.logger.debug(args)
        message_check = validate_require_param(args, {'iplist': False})
        if len(message_check) > 0:
            err_message = convert_message_to_string(message_check)
            return Response(err_message, status=400)

        ip_list = args['iplist']

        config = g.user.get_api()._api_client.service.getEntityByName(0, view, Entity.Configuration)
        if config['type'] is None:
            raise Exception('View \'{0}\' does not exist'.format(view))
        config_id = config['id']

        ip_list = ip_list.split(',')
        for ip in ip_list:
            ip = ip.strip()
            if util.is_valid_ipv4_address(ip):
                ip_address = g.user.get_api()._api_client.service.getIP4Address(config_id, ip)
            elif util.is_valid_ipv6_address(ip):
                ip_address = g.user.get_api()._api_client.service.getIP6Address(config_id, ip)
            else:
                raise Exception('Ip address \'{0}\' is invalid'.format(ip))
            id = ip_address['id']
            if id is not 0:
                g.user.get_api()._api_client.service.delete(id)
        return Response(status=200)
    except Exception as ex:
        return Response(ex.__str__(), status=400)


@route(app, '/ipam/subpool/<string:view>/<string:poolcidr>', methods=['DELETE'])
def release_subpool(view, poolcidr):
    """release subpool under configuration (view)"""
    try:
        config = g.user.get_api()._api_client.service.getEntityByName(0, view, Entity.Configuration)
        if config['type'] is None:
            raise IpPoolBadRequestException('View \'{0}\' does not exist'.format(view))
        config_id = config['id']

        poolcidr = urllib.parse.unquote(poolcidr)
        pool = find_obj_by_cidr(get_pools_under_id(config_id), poolcidr)
        if pool is None:
            raise IpPoolBadRequestException('Subpool \'{0}\' does not exist'.format(poolcidr))
        g.user.get_api()._api_client.service.delete(pool['id'])
        return Response(status=200)
    except IpPoolBadRequestException as ex:
        return Response(ex.description, status=400)


def get_gateway_under_network(network_id):
    """get gateway ip under network"""
    ip_list = g.user.get_api()._api_client.service.getEntities(network_id, Entity.IP4Address, 0, 10)
    for ip in ip_list:
        properties = properties_to_map(ip['properties'])
        state = properties['state']
        if 'GATEWAY' == state:
            return ip['id']
    return None
