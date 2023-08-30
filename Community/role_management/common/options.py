# Copyright 2023 BlueCat Networks. All rights reserved.
from flask import g

from .roles import get_role_server_id
from ..rest_v2 import common
from ..rest_v2.constants import EntityV2


def validate_existing_dns_options(role, target_zone, role_collection=None, existed_zone_options=None, option_filter=None):
    """
    Validate if the options in collections of roles exist in target zones
    If existing at least one, return the first option which is conflicted
    Else continue the action step
    Return list of option in role's collection if there is no duplicated option
    :param role: deployment role to copy/move
    :param target_zone: target zones to which the roles and options are copied
    :param role_collection: role collection
    :param existed_zone_options: existed zone options
    :parm option_filter: filter which option will be copied
    """
    rest_v2 = g.user.v2
    collection = common.get_parent_entity_of_role(role) if not role_collection \
        else {
        'id': role_collection.get('id'),
        'type': EntityV2.get_collection(role_collection.get('type')),
    }
    if not collection or collection.get('id') == target_zone.get('id'):
        return []
    collection_id = collection.get('id')
    collection_type = collection.get('type')
    target_zone_collection = EntityV2.get_collection(target_zone.get('type'))
    options_in_role = rest_v2.get_deployment_options_by_collection(collection_type, collection_id).get('data')
    new_options_in_role = []
    for option in options_in_role:
        for i in range(0, len(option_filter)):
            if option.get("name") == option_filter[i].get("name"):
                opt_value = option_filter[i].get("value")
                if opt_value and option.get("value") != opt_value:
                    continue
                new_options_in_role.append(option)
                break
    options_in_role = new_options_in_role
    options_in_zone = rest_v2.get_deployment_option_by_collection(
        target_zone_collection, target_zone.get('id'),
        fields='id, name, type, _inheritedFrom, definition, serverScope'
    ).get('data') if existed_zone_options is None else existed_zone_options
    options_in_role = [option for option in options_in_role if validate_option_and_role_server(option, role)]
    options_in_zone = [option for option in options_in_zone if not option.get('_inheritedFrom')]
    option_names_in_role = dict()
    for role_option in options_in_role:
        option_name = role_option.get('name')
        server_scope = get_server_scope_id_of_option(role_option)
        if option_names_in_role.get(option_name):
            option_names_in_role[option_name].append(server_scope)
        else:
            option_names_in_role[option_name] = [server_scope]
    if not option_names_in_role or not options_in_zone:
        return options_in_role
    for option in options_in_zone:
        server_scope = get_server_scope_id_of_option(option)
        option_name = option.get('name')
        if option_name in option_names_in_role and server_scope in option_names_in_role.get(option_name):
            display_name = common.get_display_option_name(option)
            zone_type = target_zone.get('type')
            zone_name = target_zone.get('range') \
                if zone_type in (EntityV2.IP4_NETWORK, EntityV2.IP6_NETWORK, EntityV2.IP6_BLOCK, EntityV2.IP4_BLOCK) \
                else target_zone.get('absoluteName')
            return {
                'option_name': display_name,
                'zone_type': zone_type,
                'zone_name': zone_name
            }
    return options_in_role


def validate_option_and_role_server(dns_option, role):
    if not dns_option.get('serverScope'):
        return True
    rest_v2 = g.user.v2
    server_id = get_role_server_id(role)
    server_scope = dns_option.get('serverScope')
    if server_scope.get('type') == EntityV2.SERVER and server_scope.get('id') == server_id:
        return True
    elif server_scope.get('type') == EntityV2.SERVER_GROUP:
        server_in_server_group = rest_v2.get_servers_in_server_group(server_scope.get('id'),
                                                                     filters='id: {}'.format(server_id))
        if server_in_server_group.get('count', 0) > 0:
            return True
    return False


def get_server_scope_id_of_option(option):
    server_scope = option.get('serverScope')
    if not server_scope:
        return ''
    return server_scope.get('id', '')
