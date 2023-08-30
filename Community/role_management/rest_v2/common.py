# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
import copy
import json
import re

from flask import g
from itertools import groupby

from .constants import (
    GroupOption,
    RoleType,
    Collections,
    RoleGroup,
    ZoneTypeCls,
    EntityV2, ALLOW_TARGET_COLLECTION, Actions
)
from ..common import common
from ..common.exception import InvalidParam


def get_links_href(links, name='self'):
    if not links or not links.get(name):
        return ''
    return links.get(name).get('href')


def get_collection(entity):
    result = ''
    try:
        result = entity.get("_links").get("collection").get("href")
    except Exception as e:
        g.user.logger.warning(f'Get collection exception: {e}')
    return result


def get_server_of_interface(api, interface):
    server_entity = {}
    try:
        collection = get_collection(interface)
        if collection:
            server_id = re.search('servers/(.*)/interfaces', collection).group(1)
            server_entity = api.get_entity_by_id(server_id, link=False)
    except Exception as e:
        g.user.logger.warning(f"Get server of interface exception: {e}")
    return server_entity


def get_parent_entity_of_role(role):
    collection = get_collection(role)
    response = {}
    try:
        entity_type = collection.split('/')[3]
        entity_id = collection.split('/')[4]
        response = {
            'id': entity_id,
            'type': entity_type
        }
    except Exception as e:
        g.user.logger.warning(f'Get role parent entity exception: {e}')
    return response


def get_view_of_zone(api, zone):
    view_id = 0
    try:
        collection = get_collection(zone)
        if "views" in collection:
            view_id = collection.split('/')[4]
        else:
            zone = api.get_entity_by_id(collection.split('/')[4])
            view_id = get_view_of_zone(api, zone)
    except Exception as e:
        g.user.logger.warning(f'Get view of zone exception: {e}')
    return view_id


def load_entity(entity):
    response = {
        "id": entity.get('id'),
        "name": entity.get('name'),
        "type": entity.get('type')
    }
    return response if entity else {}


def load_zone(entity):
    response = {
        "id": entity.get('id'),
        "name": entity.get('name'),
        "absoluteName": entity.get('absoluteName'),
        "type": entity.get('type')
    }
    return response if entity else {}


def load_network(network):
    response = {}
    try:
        reverse_name = common.get_reverse_zone_name(network.get('range'))
        response = {
            "id": network.get('id'),
            "name": network.get('name'),
            "type": network.get('type'),
            "range": network.get('range'),
            "reverseZoneName": reverse_name,
        }
        if 'v4' in response.get('type'):
            response.update({"view": load_entity(network.get('defaultView'))})
    except Exception as e:
        g.user.logger.warning(f"Load network exception: {e}")
    return response


def load_role(role):
    response = {}
    try:
        response = {
            "id": role.get('id'),
            "name": role.get('name'),
            "type": role.get('type'),
            "serverInterface": load_entity(role.get('serverInterface')),
            "zoneTransferServerInterface": role.get('zoneTransferServerInterface')
        }
    except Exception as e:
        g.user.logger.warning(f"Load role exception: {e}")
    return response


def get_server_of_role(api, role):
    server_entity: dict = {}
    try:
        interface_id = role.get("serverInterface").get("id")
        interface_entity = api.get_entity_by_id(interface_id)
        server_entity = get_server_of_interface(api, interface_entity)
    except Exception as e:
        g.user.logger.warning(f"Get server of role exception: {e}")
    return server_entity


def list_all_roles(response, configuration_id):
    api = g.user.v2
    try:
        role_list = response.get('data')
        zone_list = api.get_zones_in_configuration(configuration_id).get('data')
        for role in role_list:
            role.update({'configuration': load_entity(role.get('configuration'))})
            role_parent = get_parent_entity_of_role(role)
            if role.get('zoneTransferServerInterface'):
                role.update({'zoneTransferServerInterface': role.get('zoneTransferServerInterface')})
            role.update({'parentEntity': role_parent.get('id')})
            if role_parent.get('type') == Collections.NETWORKS:
                role.update({'network': load_network(api.get_entity_by_id(role_parent.get('id')))})
            elif role_parent.get('type') == Collections.ZONES:
                role.update({'zone': find_zone(role_parent.get('id'), zone_list)})
            elif role_parent.get('type') == Collections.BLOCKS:
                role.update({'block': load_network(api.get_entity_by_id(role_parent.get('id')))})
            if role.get('view'):
                role.update({'view': load_entity(role.get('view'))})
            role.update({'serverInterface': role.get('serverInterface')})
            role.pop('_links')
    except Exception as e:
        g.user.logger.warning(f"List all roles exception: {e}")
        raise e
    return role_list


def find_zone(zone_id, zone_list):
    for zone in zone_list:
        if str(zone.get('id')) == zone_id:
            return load_zone(zone)


def get_parent_of_group_roles(group):
    parent = {}
    if group and isinstance(group, list):
        if 'zone' in group[0]:
            parent = group[0].get('zone')
        elif 'network' in group[0]:
            parent = group[0].get('network')
        elif 'block' in group[0]:
            parent = group[0].get('block')
        else:
            parent = group[0].get('view')
    return parent


def group_roles_by_option(role_list, option):
    result = []
    if option not in GroupOption.all():
        raise InvalidParam(f"Invalid group option: {option}")
    for role in role_list:
        if isinstance(role.get(option), dict):
            role.update({option: json.dumps(role.get(option))})
    role_list = sorted(role_list, key=lambda x: x[option])
    for key, value in groupby(role_list, lambda x: x[option]):
        entity = []
        for item in value:
            key = item.pop(option)
            entity.append(item)
        if option == GroupOption.BY_SERVER:
            key = json.loads(key)
        elif option == GroupOption.BY_PARENT:
            key = get_parent_of_group_roles(entity)
        result.append(
            {
                option: key,
                "roles": list(entity)
            }
        )
    return result


def group_by_role_of_server(role_list, start=0, count=100):
    end = start + count
    group_role_of_server_result = []
    role_group_by_server = group_roles_by_option(role_list, GroupOption.BY_SERVER)
    total = role_acc = 0
    for group in role_group_by_server:
        roles = group.get('roles')
        role_group_by_type = group_roles_by_option(roles, GroupOption.BY_ROLE)
        role_count = len(role_group_by_type)
        total += role_count
        if role_acc >= end:
            continue
        if start < total <= end:
            if total - start < role_count:
                group['roles'] = role_group_by_type[-(total-start):]
            else:
                group['roles'] = role_group_by_type
            group_role_of_server_result.append(group)
        elif total > start and total > end:
            residual = total - end
            group['roles'] = role_group_by_type[:residual]
            group_role_of_server_result.append(group)
        role_acc = total
    return group_role_of_server_result, total


def filter_role_type(role_filter):
    filter_role = ''
    if role_filter:
        type_list = role_filter.split(',')
        filter_role = 'roleType: in('
        for r_type in type_list:
            filter_role += '"{}",'.format(r_type.upper())
        filter_role = filter_role[:-1] + ')'
    return filter_role


def filter_by_interface(interface_list):
    filter_interface = ''
    if interface_list:
        filter_interface = 'serverInterface.id: in('
        for interface_id in interface_list:
            filter_interface += '{}, '.format(interface_id)
        filter_interface = filter_interface[:-2] + ')'
    return filter_interface


def filter_by_view(configuration_id, view_names):
    api = g.user.v2
    view_list = [val for val in view_names.split(',') if val]
    filter_view = ''
    filter_view_id = ''
    if view_list:
        filter_view = 'view.name: in('
        filter_view_id = 'ancestor.id: in('
        for view_name in view_list:
            view_id = api.get_view_by_name(view_name, 'ancestor.id: {}'.format(configuration_id), fields='id') \
                .get('data')[0].get('id')
            filter_view_id += '{},'.format(view_id)
            filter_view += '"{}", '.format(view_name)
        filter_view_id = filter_view_id[:-1] + ')'
        filter_view = filter_view[:-2] + ')'
    return filter_view, filter_view_id


def filter_roles(role_list, zone_names='', blocks='', networks='', interfaces='', servers=''):
    if not zone_names and not blocks and not networks and not interfaces and not servers:
        return role_list
    zone_list = [val for val in zone_names.split(',') if val]
    block_list = [val for val in blocks.split(',') if val]
    network_list = [val for val in networks.split(',') if val]
    interface_list = [val for val in interfaces.split(',') if val]
    server_list = [val for val in servers.split(',') if val]
    role_list = role_list if isinstance(role_list, list) else [role_list]
    result = []
    for role in role_list:
        role_server_interface = role.get('serverInterface')
        if interface_list and not role_server_interface.get('name') in interface_list:
            continue
        if server_list and role_server_interface.get('server') \
                and role_server_interface.get('server').get('name') not in server_list:
            continue
        if (not zone_names and not blocks and not networks)\
                or (role.get('zone') and role.get('zone').get('absoluteName') in zone_list)\
                or (role.get('block') and role.get('block').get('reverseZoneName') in block_list) \
                or (role.get('network') and role.get('network').get('reverseZoneName') in network_list):
            result.append(role)
    return result


def get_formatted_role(role):
    role['configuration'] = load_entity(role.get('configuration'))
    if role.get('view'):
        role['view'] = load_entity(role.get('view'))
    role.pop('_links')
    return role


def get_filtered_roles(role_list, zone_dict, block_dict, network_dict, view_id, interfaces='', servers='', api=None,
                       is_inherited=False, filters=''):
    if not api:
        api = g.user.v2
    used_ids = []
    interface_list = [val for val in interfaces.split(',') if val]
    server_list = [val for val in servers.split(',') if val]
    role_list = role_list if isinstance(role_list, list) else [role_list]
    result = []
    try:
        for role in role_list:
            role_parent = get_parent_entity_of_role(role)
            parent_id = role_parent.get('id')
            parent_type = role_parent.get('type')
            role['parentEntity'] = int(parent_id)
            if parent_type == Collections.NETWORKS:
                if parent_id not in network_dict:
                    continue
                used_ids.append(parent_id)
                role['network'] = load_network(network_dict.get(parent_id))
            elif parent_type == Collections.ZONES:
                if parent_id not in zone_dict:
                    continue
                used_ids.append(parent_id)
                role['zone'] = load_zone(zone_dict.get(parent_id))
            elif parent_type == Collections.BLOCKS:
                if parent_id not in block_dict:
                    continue
                used_ids.append(parent_id)
                role['block'] = load_network(block_dict.get(parent_id))
            role_server_interface = role.get('serverInterface')
            if interface_list and not role_server_interface.get('name') in interface_list:
                continue
            if server_list and role_server_interface.get('server') \
                    and role_server_interface.get('server').get('name') not in server_list:
                continue
            result.append(get_formatted_role(role))
        if is_inherited:
            left_over_collections = zone_dict | block_dict | network_dict
            origin_collection_dict = copy.deepcopy(left_over_collections)
            for _id in set(used_ids):
                left_over_collections.pop(_id, None)

            filter_str = 'view.id: {}'.format(view_id)
            if filters:
                filter_str += ' and ' + filters
            for collection in left_over_collections.values():
                collection_type = EntityV2.get_collection(collection.get('type'))
                roles = api.get_deployment_roles_by_collection(collection_type, collection.get('id'),
                                                               filters=filter_str).get('data')
                if not roles or not roles[0].get('_inheritedFrom'):
                    continue
                for role in roles:
                    role_server_interface = role.get('serverInterface')
                    if interface_list and not role_server_interface.get('name') in interface_list:
                        continue
                    if server_list and role_server_interface.get('server') \
                            and role_server_interface.get('server').get('name') not in server_list:
                        continue
                    role_parent_type = EntityV2.get_collection(collection.get('type'))
                    role['parentEntity'] = int(collection.get('id'))
                    if role_parent_type == Collections.NETWORKS:
                        role['network'] = load_network(collection)
                    elif role_parent_type == Collections.ZONES:
                        role['zone'] = load_zone(collection)
                    elif role_parent_type == Collections.BLOCKS:
                        role['block'] = load_network(collection)
                    inherited_collection = role.get('_inheritedFrom')
                    if inherited_collection:
                        inherited_id = str(inherited_collection.get('id'))
                        if inherited_id in origin_collection_dict:
                            inherited_collection = origin_collection_dict.get(inherited_id)
                        else:
                            inherited_collection = api.get_entity_by_id(inherited_id)
                        if inherited_collection.get('type') == EntityV2.ZONE:
                            inherited_collection = load_zone(inherited_collection)
                        elif inherited_collection.get('type') in (EntityV2.IP4_BLOCK, EntityV2.IP6_BLOCK,
                                                                  EntityV2.IP4_NETWORK, EntityV2.IP6_NETWORK):
                            inherited_collection = load_network(inherited_collection)
                        else:
                            inherited_collection = load_entity(inherited_collection)
                        role['_inheritedFrom'] = inherited_collection

                    result.append(get_formatted_role(role))
    except Exception as e:
        g.user.logger.warning(f"List all roles exception: {e}")
        raise e
    return result


def filter_by_configuration(api, configuration_id, role_list):
    views = api.get_views_in_configuration(configuration_id)
    result = []
    if views.get('data'):
        data = views.get('data')
        view_ids = [view.get('id') for view in data]
        for role in role_list:
            if role.get('view').get('id') in view_ids:
                result.append(role)
    return result


def move_role_to_server(api, role_id, new_server_interface_id):
    try:
        role = api.get_deployment_role(role_id)
        server_interface = {
            'id': new_server_interface_id
        }
        collection = get_parent_entity_of_role(role)
        role['serverInterface'] = server_interface
        api.delete_deployment_role(role_id)
        result = api.add_dns_deployment_role(role=role, collection=collection.get('type'),
                                             collection_id=collection.get('id'))
        return result
    except Exception as e:
        g.user.logger.error(f"Copy role to server exception: {e}")


def copy_role_to_server(api, role_id, new_server_interface_id):
    try:
        role = api.get_deployment_role(role_id)
        server_interface = {
            'id': new_server_interface_id
        }
        if role.get('roleType') == RoleType.PRIMARY:
            role.update({'roleType': RoleType.SECONDARY})
        elif role.get('roleType') == RoleType.HIDDEN_PRIMARY:
            role.update({'roleType': RoleType.STEALTH_SECONDARY})
        collection = get_parent_entity_of_role(role)
        role['serverInterface'] = server_interface
        result = api.add_dns_deployment_role(role=role, collection=collection.get('type'),
                                             collection_id=collection.get('id'))
        return result
    except Exception as e:
        g.user.logger.error(f"Copy role to server exception: {e}")


def filter_by_role_groups(role_groups):
    filter_role = ''
    if not role_groups or role_groups == RoleGroup.ALL:
        return filter_role
    if role_groups == RoleGroup.PRIMARY:
        filter_role = 'roleType: in("{}", "{}")'.format(RoleType.PRIMARY, RoleType.HIDDEN_PRIMARY)
    elif role_groups == RoleGroup.AUTHORITATIVE:
        filter_role = 'roleType: in("{}","{}","{}","{}")'.format(RoleType.PRIMARY, RoleType.HIDDEN_PRIMARY,
                                                                 RoleType.SECONDARY, RoleType.STEALTH_SECONDARY)
    elif role_groups == RoleGroup.RECURSION:
        filter_role = 'roleType: in("{}","{}")'.format(RoleType.FORWARDER, RoleType.STUB)
    elif role_groups == RoleGroup.EXPOSED:
        filter_role = 'roleType: in("{}","{}")'.format(RoleType.PRIMARY, RoleType.SECONDARY)
    elif role_groups == RoleGroup.FORWARDING:
        filter_role = 'roleType: in("{}")'.format(RoleType.FORWARDER)
    return filter_role


def get_id(response_data):
    data = response_data.get('data')[0]
    return data.get('id')


def get_deployment_roles_by_collection(cls_data, server_interface='', view=''):
    rest_v2 = g.user.v2
    role_cls = cls_data.get('type')
    role_cls_name = cls_data.get('name')
    role_cls_type = EntityV2.get_collection(role_cls)
    dep_roles = rest_v2.get_deployment_roles_by_collection(role_cls_type, cls_data.get('id')).get('data')
    if server_interface:
        dep_roles = [dep_role for dep_role in dep_roles if
                     dep_role.get('serverInterface').get('name') == server_interface]
    if view and ('Block' in role_cls or 'Network' in role_cls):
        dep_roles = [dep_role for dep_role in dep_roles if dep_role.get('view').get('name') == view]
    if not dep_roles:
        raise InvalidParam(
            'Not found deployment roles in {} group with collection: {} with collection named: {}'.format(
                RoleGroup.PRIMARY, role_cls, role_cls_name))
    return dep_roles


def get_target_collection_data(configuration_cls, action, collections):
    rest_v2 = g.user.v2
    if not isinstance(collections, list):
        collections = [collections]
    ancestor_conf = 'ancestor.id:{}'.format(configuration_cls.get('id'))
    ancestor_view = ''
    configuration_name = configuration_cls.get('name')
    cls_data = []
    for collection in collections:
        cls = collection.get('collection')
        cls_names = []
        if not cls:
            raise InvalidParam('Missing collection({}) for action named {}'.format(ALLOW_TARGET_COLLECTION, action))

        if action == Actions.COPY:
            if cls == Collections.ZONES:
                cls_names = collection.get('absolute_names')
                if not cls_names:
                    raise InvalidParam('Missing absolute names for collection {}.'.format(cls))
                view = collection.get('view')
                if not view:
                    raise InvalidParam('Missing View for Zone collection.')
                view_js = rest_v2.get_view_by_name(view, ancestor_conf)
                if view_js.get('count') == 0:
                    raise InvalidParam(
                        'View named {} was not found in configuration named {}'.format(view, configuration_name))
                ancestor_view = 'ancestor.id:{}'.format(view_js.get('data')[0].get('id'))
            elif cls in [Collections.NETWORKS, Collections.BLOCKS]:
                cls_names = collection.get('ranges')
                if not cls_names:
                    raise InvalidParam('Missing ranges for collection {}.'.format(cls))

        if action in [Actions.ADD_SERVERS, Actions.MOVE, Actions.COPY, Actions.MOVE_PRIMARY]:
            cls_names = collection.get('server_interfaces') if not cls_names else cls_names
            if collection.get('collection') == 'interfaces' and not cls_names:
                raise InvalidParam('Missing interface names for collection {} with action named {}'.format(cls, action))
            if cls != Collections.INTERFACES and action in [Actions.ADD_SERVERS, Actions.MOVE, Actions.MOVE_PRIMARY]:
                raise InvalidParam(
                    'Only support collection named {} for action named {}'.format(Collections.INTERFACES,
                                                                                  action))

        for cls_name in cls_names:
            if cls == Collections.ZONES:
                collection_rs = rest_v2.get_zone_by_name(cls_name, ancestor_view or ancestor_conf,
                                                         fields="id,name,type,absoluteName")
            elif cls == Collections.NETWORKS:
                collection_rs = rest_v2.get_network_by_range(cls_name, ancestor_conf)
            elif cls == Collections.BLOCKS:
                collection_rs = rest_v2.get_block_by_range(cls_name, ancestor_conf)
            elif cls == Collections.INTERFACES:
                collection_rs = rest_v2.get_interface_by_name(cls_name, ancestor_conf)
            else:
                raise InvalidParam('Invalid collection {}, must be in: {}'.format(cls, ALLOW_TARGET_COLLECTION))
            if collection_rs.get('count') == 0:
                raise InvalidParam(
                    'Not found collection: {} with collection named: {} in configuration named {}'.format(
                        cls, cls_name, configuration_name))
            collection_rs_data = collection_rs.get('data')[0]
            if collection.get('view'):
                collection_rs_data['view'] = collection.get('view')
            if action == Actions.ADD_SERVERS:
                collection_rs_data.update({
                    'role_type': collection.get('role_type'),
                    'zone_transfer_interface': collection.get('zone_transfer_interface')
                })
            cls_data.append(collection_rs_data)
    return cls_data


def get_collection_data(configuration_cls, role):
    rest_v2 = g.user.v2
    ancestor = 'ancestor.id:{}'.format(configuration_cls.get('id'))
    configuration_name = configuration_cls.get('name')
    role_cls = role.get('collection')
    role_cls_name = role.get('name')
    if role_cls in ZoneTypeCls.REVERSE_ZONE:
        role_cls_name = role.get('range')
        if not role_cls_name:
            raise InvalidParam("Missing Range for collection named {}.".format(role_cls))
    elif role_cls == Collections.ZONES:
        role_cls_name = role.get('absolute_name')
        if not role_cls_name:
            raise InvalidParam("Missing absolute name for Zone.")
    if not role_cls_name:
        raise InvalidParam("Missing Name for collection named View")
    collection_rs = {
        "count": 0
    }
    if role_cls in ZoneTypeCls.FORWARDER_ZONE:
        view = role.get('view')
        if role_cls == Collections.ZONES:
            if not view:
                raise InvalidParam('Missing View for Zone collection named {}'.format(role_cls_name))
            view_js = rest_v2.get_view_by_name(view, ancestor)
            if view_js.get('count') == 0:
                raise InvalidParam(
                    'View named {} was not found in configuration named {}'.format(view, configuration_name))
            ancestor = 'ancestor.id:{}'.format(view_js.get('data')[0].get('id'))
            collection_rs = rest_v2.get_zone_by_name(role_cls_name, ancestor, fields="id,name,type,absoluteName")
        else:
            collection_rs = rest_v2.get_view_by_name(role_cls_name, ancestor)

    elif role_cls == Collections.NETWORKS:
        collection_rs = rest_v2.get_network_by_range(role_cls_name, ancestor)
    elif role_cls == Collections.BLOCKS:
        collection_rs = rest_v2.get_block_by_range(role_cls_name, ancestor)

    if collection_rs.get('count') == 0:
        raise InvalidParam(
            'Not found collection: {} with collection named: {} in configuration named {}'.format(
                role_cls,
                role_cls_name,
                configuration_name))
    cls_data = collection_rs.get('data')[0]
    return cls_data


def get_display_option_name(option):
    rest_v2 = g.user.v2
    display_name = ''
    try:
        definition_href = get_links_href(option.get('definition').get('_links'))
        display_name = rest_v2.link_api(definition_href, fields='displayName').get('displayName')
    except Exception as e:
        g.user.logger.warning(
            'Failed to get display name of DNS Option {}: {}'.format(option.get('name'), str(e)))
    return display_name


def get_deployment_options_by_collection(cls_data):
    rest_v2 = g.user.v2
    role_cls = cls_data.get('type')
    role_cls_type = EntityV2.get_collection(role_cls)
    dep_options = rest_v2.get_deployment_options_by_collection(role_cls_type, cls_data.get('id'))
    return dep_options
