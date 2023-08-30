# Copyright 2023 BlueCat Networks. All rights reserved.
from bluecat.entity import Entity
from flask import g

from .constants import DeploymentRoleInterfaceType
from .exception import ActionConflictException, InvalidZoneTransferInterfaceException

from ..rest_v2.common import get_collection, get_parent_entity_of_role
from ..rest_v2.constants import RECURSIVE_ROLES, RoleType, EntityV2


def get_duplicate_role_by_server(current_role, interface_id, collection=None):
    """
    Get any DNS Deployment Role of same collection in current server
    :param current_role: DNS Deployment Role object
    :param interface_id: server interface id
    :param collection: optional role collection
    :return: role of same collection in current server if exists
    """
    rest_v2 = g.user.v2
    if collection:
        collection_type = EntityV2.get_collection(collection.get('type'))
        collection_id = collection.get('id')
    else:
        cls = get_parent_entity_of_role(current_role)
        collection_type, collection_id = cls.get('type'), cls.get('id')
    roles_of_collection = rest_v2.get_deployment_roles_by_collection(collection_type, collection_id).get(
        'data')
    for role in roles_of_collection:
        if role.get('_inheritedFrom'):
            return {}
        if role.get('serverInterface').get('id') == interface_id:
            return role
    return {}


def get_duplicate_role_in_zone(new_zone, interface_id):
    """
    Check if there is any DNS Deployment Role of same server interface in current zone
    :param new_zone: Zone/IPv(4/6) Block/IPv(4/6) Network
    :param interface_id: server interface id
    :return: role of same server in current zone if exists
    """
    rest_v2 = g.user.v2
    zone_type = new_zone.get('type')
    roles_of_collection = rest_v2.get_deployment_roles_by_collection(EntityV2.get_collection(zone_type),
                                                                     new_zone.get('id')).get('data')
    for role in roles_of_collection:
        if role.get('_inheritedFrom'):
            return {}
        if role.get('serverInterface').get('id') == interface_id:
            return role
    return {}


def convert_primary_role(role):
    """
    convert PRIMARY role to SECONDARY and HIDDEN PRIMARY to STEALTH SECONDARY
    :param role: DNS Deployment Role object
    :return: DNS Deployment Role object
    """
    if role.get('roleType') == RoleType.PRIMARY:
        role['roleType'] = RoleType.SECONDARY
    elif role.get('roleType') == RoleType.HIDDEN_PRIMARY:
        role['roleType'] = RoleType.STEALTH_SECONDARY
    return role


def get_merge_role_result(current_role_type, duplicate_role_type):
    if current_role_type in RECURSIVE_ROLES or duplicate_role_type in RECURSIVE_ROLES:
        if current_role_type == duplicate_role_type:
            return current_role_type
        raise ActionConflictException("Conflicted. Cannot merge role {} with {}".format(current_role_type,
                                                                                        duplicate_role_type))
    if current_role_type == duplicate_role_type:
        return current_role_type
    priority_role = {
        RoleType.STEALTH_SECONDARY: 1,
        RoleType.HIDDEN_PRIMARY: 2,
        RoleType.SECONDARY: 2,
        RoleType.PRIMARY: 3,
    }
    current_role_priority = priority_role[current_role_type]
    duplicate_role_priority = priority_role[duplicate_role_type]
    if current_role_priority == 2 and duplicate_role_priority == 2:
        return RoleType.PRIMARY

    if duplicate_role_priority > current_role_priority:
        return duplicate_role_type
    return current_role_type


def create_deployment_role_object(configuration_cls, view_name, role_type, server_interface, zone_transfer_interface):
    api = g.user.v2
    fields = 'id, name, type, _links'
    ancestor_filter = 'ancestor.id: {}'.format(configuration_cls.get('id'))
    view_cls = api.get_view_by_name(view_name, filter=ancestor_filter, fields=fields).get('data')[0]
    interface_cls = api.get_interface_by_name(server_interface, filter=ancestor_filter, fields=fields).get('data')[0]
    interface_cls['deploymentRoleInterfaceType'] = DeploymentRoleInterfaceType.SERVICE
    role_cls = {
        'name': role_type.replace('_', ' ').title(),
        'roleType': role_type.upper(),
        'configuration': configuration_cls,
        'serverInterface': interface_cls,
        'type': Entity.DeploymentRole,
        'view': view_cls
    }
    if zone_transfer_interface:
        zone_transfer_interface_cls = api.get_interface_by_name(zone_transfer_interface, filter=ancestor_filter,
                                                                fields=fields).get('data')[0]
        if get_collection(zone_transfer_interface_cls) == get_collection(interface_cls):
            raise InvalidZoneTransferInterfaceException(
                f"Main Interface {server_interface} and Zone Transfers Interface"
                f" {zone_transfer_interface} can't be the same server")
        role_type = role_type.upper()
        if role_type in (RoleType.SECONDARY, RoleType.STEALTH_SECONDARY):
            zone_transfer_interface_cls['deploymentRoleInterfaceType'] = DeploymentRoleInterfaceType.ZONE_TRANSFER
        elif role_type in (RoleType.STUB, RoleType.FORWARDER):
            zone_transfer_interface_cls['deploymentRoleInterfaceType'] = DeploymentRoleInterfaceType.TARGET
        role_cls['zoneTransferServerInterface'] = zone_transfer_interface_cls
    return role_cls


def get_service_interfaces_and_zone_transfer_interface(role_id):
    api = g.user.v2
    interface_response = api.get_deployment_role_interfaces(role_id,
                                                            fields='id, name, type, '
                                                                   'server.id, server.name, server.type,'
                                                                   ' deploymentRoleInterfaceType')
    if not interface_response.get('count'):
        return None, None
    interfaces = interface_response.get('data')
    service_interface = zone_transfer_interface = None
    for interface in interfaces:
        if interface.get('deploymentRoleInterfaceType') == DeploymentRoleInterfaceType.SERVICE:
            service_interface = interface
        else:
            zone_transfer_interface = interface
    return service_interface, zone_transfer_interface


def get_API_formatted_role(role):
    role_type = role.get('roleType', '').upper()
    role_interface = role.get('serverInterface')
    role_interface['deploymentRoleInterfaceType'] = DeploymentRoleInterfaceType.SERVICE
    interface_list = [role_interface]
    zone_transfer_interface = role.get('zoneTransferServerInterface')
    if zone_transfer_interface and role_type in (RoleType.SECONDARY, RoleType.STEALTH_SECONDARY):
        zone_transfer_interface['deploymentRoleInterfaceType'] = DeploymentRoleInterfaceType.ZONE_TRANSFER
        interface_list.append(zone_transfer_interface)
    elif zone_transfer_interface and role_type in (RoleType.STUB, RoleType.FORWARDER):
        zone_transfer_interface['deploymentRoleInterfaceType'] = DeploymentRoleInterfaceType.TARGET
        interface_list.append(zone_transfer_interface)
    role['interfaces'] = interface_list
    return role


def validate_valid_zone_transfer_and_target_interface(role, target_interface):
    if isinstance(target_interface, int) or isinstance(target_interface, str):
        target_interface = g.user.v2.get_interface(target_interface)
    if role.get('roleType') in [RoleType.PRIMARY, RoleType.HIDDEN_PRIMARY, RoleType.NONE] \
            or not role.get('zoneTransferServerInterface'):
        return True
    if validate_interfaces_from_different_server(target_interface, role.get('zoneTransferServerInterface')):
        return True
    return False


def validate_interfaces_from_different_server(interface1, interface2):
    rest_v2 = g.user.v2
    server1 = interface1.get('server', {}).get('id')
    server2 = interface2.get('server', {}).get('id')
    if not server1:
        server1 = rest_v2.get_interface(interface1.get('id')).get('server').get('id')
    if not server2:
        server1 = rest_v2.get_interface(interface2.get('id')).get('server').get('id')
    return server1 != server2


def get_role_server_id(role):
    interface = role.get('serverInterface')
    rest_v2 = g.user.v2
    server_id = interface.get('server', {}).get('id')
    if not server_id:
        server_id = rest_v2.get_interface(interface.get('id')).get('server').get('id')
    return server_id


def to_display_rt(role_type):
    return role_type.replace('_', ' ').title()
