# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
import copy
import traceback

from flask import g

from .constants import Status
from .exception import InvalidZoneTransferInterfaceException, InvalidParam
from .options import validate_existing_dns_options
from .roles import (
    create_deployment_role_object,
    validate_valid_zone_transfer_and_target_interface,
    validate_interfaces_from_different_server, to_display_rt,
)

from ..rest_v2 import common
from ..rest_v2.constants import (
    RoleType,
    HIDE_ROLES,
    EXPOSE_ROLES,
    Collections,
    EntityV2,
    Actions,
    AUTHORITATIVE_ROLES,
    RECURSIVE_ROLES
)
from ..common.common import get_reverse_zone_name, get_collection_name


class RoleValidation:
    def __init__(self, action):
        self.action = action

    def check_duplicate_role_in_server(self, current_role, new_server_interface_id):
        """
        Check if there is any DNS Deployment Role of same collection in current server
        :param current_role: DNS Deployment Role object
        :param new_server_interface_id: server interface id

        :return: role of same collection in current server if exists
        """
        rest_v2 = g.user.v2
        collection = EntityV2.get_collection(self.collection.get('type'))
        collection_id = self.collection.get('id')
        roles_of_collection = rest_v2.get_deployment_roles_by_collection(collection, collection_id).get('data')
        result = dict()
        if not roles_of_collection:
            return result
        for role in roles_of_collection:
            if role.get('_inheritedFrom'):
                return {}
            if role.get('serverInterface').get('id') == new_server_interface_id:
                return role
        return result

    def check_duplicate_role_in_zone(self, new_zone, server_interface_id):
        """
        Check if there is any DNS Deployment Role of same server interface in current zone
        :param new_zone: New Zone, IPV4 Block, IPv4 Network
        :param server_interface_id: server interface id
        :return: role of same server in current zone if exists
        """
        rest_v2 = g.user.v2
        zone_type = new_zone.get('type')
        roles_of_collection = rest_v2.get_deployment_roles_by_collection(EntityV2.get_collection(zone_type),
                                                                         new_zone.get('id')).get('data')
        result = dict()
        for role in roles_of_collection:
            if role.get('_inheritedFrom'):
                return {}
            if role.get('serverInterface').get('id') == server_interface_id:
                return role
        return result

    def validate_duplicate_collection_roles(self, check_role, role_list):
        """
        Check if multiple roles of collection are copied to same server
        :param check_role: DNS Deployment Role to check duplicate collection
        :param role_list: list of DNS Deployment Role objects
        :return: list of DNS Deployment Role objects and validation status
        """
        check_role_collection = check_role.get('collection')
        roles = [role for role in role_list if role != check_role]
        for role in roles:
            role_cls = role.get('collection')
            if role_cls == Collections.VIEWS:
                if role.get('name') == check_role.get('name'):
                    check_role.update({
                        'message': "Duplicate in view {}".format(check_role.get("name")),
                        'status': Status.DUPLICATED
                    })
                    return check_role
            elif role_cls == Collections.ZONES:
                if role.get("absolute_name") == check_role.get("absolute_name") \
                        and role.get("view") == check_role.get("view"):
                    check_role.update({
                        'message': "Duplicate in zone {}({})".format(check_role.get("absolute_name"),
                                                                     check_role.get("view")),
                        'status': Status.DUPLICATED
                    })
                    return check_role
            elif role_cls == Collections.BLOCKS and check_role_collection == Collections.BLOCKS:
                if role.get("range") == check_role.get("range"):
                    check_role.update({
                        'message': "Duplicate in block {}".format(check_role.get("range")),
                        'status': Status.DUPLICATED
                    })
                    return check_role
            elif role_cls == Collections.NETWORKS and check_role_collection == Collections.NETWORKS:
                if role.get("range") == check_role.get("range"):
                    check_role.update({
                        'message': "Duplicate in network {}".format(check_role.get("range")),
                        'status': Status.DUPLICATED
                    })
                    return check_role
        return check_role

    def validate_existing_origin_role_from_inherited(self, role):
        inherited_collection = role.get('_inheritedFrom')
        rest_v2 = g.user.v2
        for raw_role in self.raw_roles:
            if raw_role.get('collection') == EntityV2.get_collection(inherited_collection.get('type')) \
                    and role.get('roleType') == raw_role.get('role_type', '').upper() \
                    and role.get('serverInterface', {}).get('name') == raw_role.get('server_interface'):
                if inherited_collection.get('type') == EntityV2.VIEW \
                        and raw_role.get('view') == inherited_collection.get('name'):
                    return True
                else:
                    inherited_collection_data = rest_v2.get_entity_by_id(inherited_collection.get('id'), False)
                    inherited_collection_type = inherited_collection_data.get('type')
                    if inherited_collection_type == EntityV2.ZONE \
                            and raw_role.get('absolute_name') == inherited_collection_data.get('absoluteName') \
                            and raw_role.get('view') == inherited_collection_data.get('view', {}).get('name'):
                        return True
                    elif inherited_collection_type in (EntityV2.IP4_NETWORK, EntityV2.IP6_NETWORK,
                                                       EntityV2.IP4_BLOCK, EntityV2.IP6_BLOCK) \
                            and raw_role.get('range') == inherited_collection_data.get('range'):
                        return True

        return False

    def get_merge_role_validation(self, role, duplicated_role, converted=False):
        """
        Validate when merging role with existing role
        :param role: DNS Deployment Role to validate
        :param duplicated_role: existing DNS Deployment Role
        :param converted: if the role is converted
        :return: role dictionary with status and message fields if conflicting,
        otherwise return origin role without these fields
        """
        current_role_type = role.get('roleType')
        duplicated_role_type = duplicated_role.get('roleType')
        if not converted and current_role_type == duplicated_role_type:
            role.update({
                'status': Status.INFO,
                'message': f'Role {to_display_rt(current_role_type)} already exists',
                'target_role_type': current_role_type,
            })
            return role
        if (current_role_type in RECURSIVE_ROLES and current_role_type != duplicated_role_type) \
                or \
                (current_role_type in RECURSIVE_ROLES and duplicated_role.get('roleType') in AUTHORITATIVE_ROLES) \
                or \
                (current_role_type in AUTHORITATIVE_ROLES and duplicated_role_type in RECURSIVE_ROLES):
            role.update({
                'status': Status.CONFLICTED,
                'message': f'Merge conflict between role type {to_display_rt(current_role_type)} '
                           f'and {to_display_rt(duplicated_role_type)}',
                'target_role_type': current_role_type,
            })
            return role

        target_role_type = ''
        if duplicated_role_type == RoleType.STEALTH_SECONDARY:
            if current_role_type in (RoleType.PRIMARY, RoleType.SECONDARY, RoleType.HIDDEN_PRIMARY):
                target_role_type = current_role_type
        elif duplicated_role_type == RoleType.HIDDEN_PRIMARY:
            if current_role_type in (RoleType.SECONDARY, RoleType.PRIMARY):
                target_role_type = RoleType.PRIMARY
            elif current_role_type == RoleType.STEALTH_SECONDARY:
                target_role_type = RoleType.HIDDEN_PRIMARY
        elif duplicated_role_type == RoleType.SECONDARY:
            if current_role_type in (RoleType.PRIMARY, RoleType.HIDDEN_PRIMARY):
                target_role_type = RoleType.PRIMARY
            elif current_role_type == RoleType.STEALTH_SECONDARY:
                target_role_type = RoleType.SECONDARY
        elif duplicated_role_type == RoleType.PRIMARY:
            target_role_type = RoleType.PRIMARY

        if not target_role_type:
            target_role_type = current_role_type
        role.update({
            'target_role_type': target_role_type,
            'message': f'Able to merge role {to_display_rt(current_role_type)} '
                       f'with {to_display_rt(duplicated_role_type)} to {to_display_rt(target_role_type)}'
        })
        return role

    def validate_copy_move_actions(self, role, target, skip_option_validation=True):
        """
        Validate when copying or moving role to a target collection
        :param role: DNS Deployment Role to validate
        :param target: target collection
        :param skip_option_validation: Whether to skip the validation for existing dns options
        :return: role dictionary with status and message fields if conflicting,
        otherwise return origin role without these fields
        """
        try:
            rest_v2 = g.user.v2
            if role.get('status'):
                return role
            role_type = role.get('roleType')
            if target.get('type') in (EntityV2.ZONE, EntityV2.IP4_BLOCK, EntityV2.IP4_NETWORK, EntityV2.IP6_BLOCK,
                                      EntityV2.IP6_NETWORK):
                roles_of_target_collection = rest_v2.get_deployment_roles_by_collection(
                    EntityV2.get_collection(target.get('type')), target.get('id')).get('data')
                if_zone_contain_inherited_role = False
                for target_role in roles_of_target_collection:
                    if target_role.get('_inheritedFrom'):
                        if_zone_contain_inherited_role = True
                        break
                    target_role_type = target_role.get('roleType')
                    current_role_type = role.get('roleType')
                    if role.get('id') == target_role.get('id') \
                            or \
                            (target_role_type in [RoleType.PRIMARY, RoleType.HIDDEN_PRIMARY]
                             and current_role_type in [RoleType.PRIMARY, RoleType.HIDDEN_PRIMARY]
                             and target_role.get('serverInterface').get('id') != role.get('serverInterface').get('id')):
                        role.update({
                            'target_role_type': target_role_type,
                            'status': Status.INFO,
                            'message': f'{to_display_rt(target_role_type)} Role exists in target zone'
                        })
                        if target.get('id') == self.collection.get('id') and self.action == Actions.COPY:
                            target_type = target.get('type')
                            target_name = get_collection_name(target)
                            role['message'] = 'Ignore copying {} role to its collection {} {}'\
                                .format(to_display_rt(role_type), target_type, target_name)
                        return role
                if not skip_option_validation:
                    existing_option = validate_existing_dns_options(role, target, self.collection)
                    if isinstance(existing_option, dict) and existing_option.get('option_name'):
                        option_name = existing_option.get('option_name')
                        zone_type = existing_option.get('zone_type')
                        zone_name = existing_option.get('zone_name')
                        role.update({
                            'status': Status.CONFLICTED,
                            'message': "DNS Option {} already exists in {} {}".format(option_name, zone_type, zone_name)
                        })
                        return role

                duplicated_role = self.check_duplicate_role_in_zone(
                    new_zone=target,
                    server_interface_id=role.get('serverInterface').get('id'))
                if duplicated_role:
                    role = self.get_merge_role_validation(role=role, duplicated_role=duplicated_role)
                if if_zone_contain_inherited_role and (not role.get('status') or role.get('status') == Status.AVAILABLE):
                    target_type = target.get('type')
                    target_name = get_collection_name(target)
                    action = self.action.lower()
                    if self.action == Actions.ADD_SERVERS:
                        action = 'add server'
                    available_message = 'Able to {} role {}'.format(action, to_display_rt(role_type))
                    role.update({
                        'status': Status.WARNING,
                        'message': '{}  \nWARNING: All of inherited roles in {} {} in will be removed'
                        .format(role.get('message', available_message), target_type, target_name),
                    })
            else:
                if self.action == Actions.MOVE:
                    action = 'moving'
                else:
                    action = 'copying'

                if role.get('_inheritedFrom'):
                    role.update({
                        'status': Status.INFO,
                        'message': f"Skip {action} to server since it's the inherited role"
                    })
                    return role

                if role.get('serverInterface', {}).get('id') == target.get('id') and not role.get('_inheritedFrom'):
                    role.update({
                        'status': Status.INFO,
                        'message': f"Ignore {action} role {to_display_rt(role_type)} to the same interface"
                    })
                    return role
                if not validate_valid_zone_transfer_and_target_interface(role, target):
                    role.update({
                        'status': Status.INFO,
                        'message': f"Ignore {action} role {to_display_rt(role_type)} "
                                   f"to the same server with zone transfer interface"
                    })
                    return role
                if action == 'copying' and not validate_interfaces_from_different_server(role.get('serverInterface'), target):
                    role.update({
                        'status': Status.INFO,
                        'message': f"Ignore {action} role {to_display_rt(role_type)} to the same server"
                    })
                    return role

                is_converted = False

                if self.action == Actions.COPY and role_type in (RoleType.PRIMARY, RoleType.HIDDEN_PRIMARY):
                    role['roleType'] = RoleType.SECONDARY if role.get('roleType') == RoleType.PRIMARY \
                        else RoleType.STEALTH_SECONDARY
                    is_converted = True
                elif self.action == Actions.MOVE and role_type == RoleType.HIDDEN_PRIMARY:
                    role['roleType'] = RoleType.STEALTH_SECONDARY
                    is_converted = True

                duplicated_role = self.check_duplicate_role_in_server(
                    current_role=role,
                    new_server_interface_id=target.get('id'))
                if duplicated_role:
                    role = self.get_merge_role_validation(role=role, duplicated_role=duplicated_role,
                                                          converted=is_converted)
                if is_converted and not role.get('target_role_type'):
                    role['target_role_type'] = role['roleType']

                if role.get('_inheritedFrom') and (not role.get('status') or role.get('status') == Status.AVAILABLE):
                    collection = self.collection
                    collection_type = collection.get('type')
                    collection_name = get_collection_name(collection)
                    available_message = 'Able to {} role {}'.format(self.action.lower(), to_display_rt(role_type))
                    role.update({
                        'status': Status.WARNING,
                        'message': '{}  \nWARNING: All of inherited roles in {} {} in will be removed'
                        .format(role.get('message', available_message), collection_type, collection_name),
                    })
            if not len(role.get('message', '')) and not role.get('status'):
                action = self.action.lower()
                if self.action == Actions.ADD_SERVERS:
                    action = 'add server'
                role['message'] = f"Able to {action} role {to_display_rt(role.get('roleType'))}"
        except Exception as e:
            g.user.logger.error("Unexpected validation on action copy/move: {}".format(e))
            g.user.logger.error(traceback.format_exc())
            role.update({
                'message': 'Unexpected error {}'.format(str(e)),
                'status': Status.UNAVAILABLE
            })
        return role

    def validate_add_servers(self, role, collection):
        """
        Validate when adding servers from a role
        :param role: DNS Deployment Role to validate add server role
        :param collection: collection to add server roles
        :return: role dictionary with status and message fields if conflicting,
        otherwise return origin role without these fields
        """
        try:
            if role.get('status'):
                return role
            role = create_deployment_role_object(role_type=role.get('role_type'),
                                                 configuration_cls=role.get('configuration'),
                                                 view_name=role.get('view'),
                                                 server_interface=role.get('server_interface'),
                                                 zone_transfer_interface=role.get('zone_transfer_interface'))

            if role.get('roleType') not in (RoleType.STEALTH_SECONDARY, RoleType.SECONDARY, RoleType.FORWARDER,
                                            RoleType.STUB):
                role.update({
                    'status': Status.CONFLICTED,
                    'message': 'Role type must be Stealth Secondary, Secondary, Forwarder or Stub'
                })
                return role
            copy_validation_result = self.validate_copy_move_actions(role, collection)
            if copy_validation_result.get('target_role_type'):
                role['target_role_type'] = copy_validation_result.get('target_role_type')
            role['message'] = copy_validation_result.get('message')
            if copy_validation_result.get('status') in [Status.CONFLICTED, Status.UNAVAILABLE]:
                role.update({
                    'status': copy_validation_result.get('status'),
                })
        except InvalidZoneTransferInterfaceException as e:
            g.user.logger.error(str(e))
            role.update({
                'message': str(e.msg),
                'status': Status.CONFLICTED
            })
        except Exception as e:
            g.user.logger.error("Unexpected error while validating on action add servers: {}".format(e))
            g.user.logger.error(traceback.format_exc())
            role.update({
                'message': 'Unexpected error: {}'.format(str(e)),
                'status': Status.UNAVAILABLE
            })
        return role

    def validate_move_primary(self, role, target):
        """
        Validate when doing action move primary roles
        :param role: DNS Deployment Role to validate
        :param target: target server
        :return: role dictionary with status and message fields if conflicting,
        otherwise return origin role without these fields
        """
        try:
            if role.get('status'):
                return role
            rest_v2 = g.user.v2
            collection = EntityV2.get_collection(self.collection.get('type'))
            collection_id = self.collection.get('id')
            roles_of_collection = rest_v2.get_deployment_roles_by_collection(collection, collection_id).get('data')
            duplicated_role = dict()
            if_zone_contain_inherited_role = False
            for cls_role in roles_of_collection:
                if cls_role.get('_inheritedFrom'):
                    if_zone_contain_inherited_role = True
                    break
                if cls_role.get('serverInterface').get('id') == target.get('id'):
                    duplicated_role = cls_role

            duplicated_role_type = duplicated_role.get('roleType')
            if duplicated_role and duplicated_role_type in (RoleType.STUB, RoleType.FORWARDER):
                role.update({
                    'status': Status.CONFLICTED,
                    'message': f'Conflicted with Recursive role'
                })
                return role

            target_role_type = RoleType.HIDDEN_PRIMARY
            if duplicated_role and duplicated_role_type in (RoleType.SECONDARY, RoleType.PRIMARY):
                target_role_type = RoleType.PRIMARY

            role.update({
                'target_role_type': target_role_type,
                'message': 'Able to move primary to interface {}'.format(target.get('name'))
            })
            if if_zone_contain_inherited_role:
                collection = self.collection
                collection_type = collection.get('type')
                collection_name = get_collection_name(collection)

                role.update({
                    'status': Status.WARNING,
                    'message': '{}\nWARNING: All of inherited roles in {} {} in will be removed'
                    .format(role.get('message', ''), collection_type, collection_name)
                })
        except Exception as e:
            g.user.logger.error("Unexpected error while validating on action move primary: {}".format(e))
            g.user.logger.error(traceback.format_exc())
            role.update({
                'message': 'Unexpected error: {}'.format(str(e)),
                'status': Status.UNAVAILABLE
            })
        return role

    def validate_hide_expose_actions(self, role):
        """
        Validate when doing action hide or expose
        :param role: DNS Deployment Role to validate
        :return: role dictionary with status and message fields if conflicting,
        otherwise return origin role without these fields
        """
        try:
            if role.get('status'):
                return role
            role_type = role.get('roleType')
            if role.get('_inheritedFrom') and not self.validate_existing_origin_role_from_inherited(role):
                role.update({
                    'status': Status.CONFLICTED,
                    'message': 'Cannot make {} for inherited role'.format('visible' if self.action == Actions.EXPOSE
                                                                          else 'hidden')
                })
                return role
            if role_type not in AUTHORITATIVE_ROLES:
                role.update({
                    'status': Status.CONFLICTED,
                    'message': 'The role is not an Authoritative role'
                })
                return role

            if self.action == Actions.HIDE and role_type in HIDE_ROLES:
                role.update({
                    'status': Status.INFO,
                    'message': f'Skip hiding {to_display_rt(role_type)} role since it is already hidden'
                })
                return role
            if self.action == Actions.EXPOSE and role_type in EXPOSE_ROLES:
                role.update({
                    'status': Status.INFO,
                    'message': f'Skip making visible {to_display_rt(role_type)} role since it is already expose'
                })
                return role
            if self.action == Actions.EXPOSE:
                role['target_role_type'] = RoleType.PRIMARY if role_type == RoleType.HIDDEN_PRIMARY \
                    else RoleType.SECONDARY
                role['message'] = f'Able to make visible role {to_display_rt(role_type)} ' \
                                  f'to {to_display_rt(role.get("target_role_type"))}'
            elif self.action == Actions.HIDE:
                role['target_role_type'] = RoleType.HIDDEN_PRIMARY if role_type == RoleType.PRIMARY \
                    else RoleType.STEALTH_SECONDARY
                role['message'] = f'Able to hide role {to_display_rt(role_type)} to ' \
                                  f'{to_display_rt(role.get("target_role_type"))}'
        except Exception as e:
            g.user.logger.error("Unexpected error while validating on action {}: {}".format(self.action.lower(), e))
            g.user.logger.error(traceback.format_exc())
            role.update({
                'message': 'Unexpected error: {}'.format(str(e)),
                'status': Status.UNAVAILABLE
            })
        return role

    def validate_delete_actions(self, role):
        """
        Validate when doing action hide or expose
        :param role: DNS Deployment Role to validate
        :return: role dictionary with status and message fields if conflicting,
        otherwise return origin role without these fields
        """
        try:
            if role.get('status'):
                return role
            is_able_to_delete = role.get('_inheritedFrom') \
                                and not self.validate_existing_origin_role_from_inherited(role)
            role.update({
                'status': Status.CONFLICTED if is_able_to_delete else Status.AVAILABLE,
                'message': "Cannot delete inherited role" if is_able_to_delete else "Able to delete role"
            })
        except Exception as e:
            g.user.logger.error("Unexpected error while validating on action {}: {}".format(self.action.lower(), e))
            g.user.logger.error(traceback.format_exc())
            role.update({
                'message': 'Unexpected error: {}'.format(str(e)),
                'status': Status.UNAVAILABLE
            })
        return role

    def validate(self, roles, target, configuration):
        """
        Validate when doing action hide or expose
        :param roles: DNS Deployment Role to validate
        :param target: list of target collection
        :param configuration: configuration object
        :return: validation result
        """
        result = []
        self.raw_roles = roles
        self.configuration = configuration
        for role in roles:
            deployment_role = {}
            try:
                role_type = role.get('role_type').upper() if role.get('role_type') else ''
                server_interface = role.get('server_interface')
                view = role.get('view')
                collection_data = common.get_collection_data(configuration_cls=configuration, role=role)
                self.collection = collection_data
                dep_roles = common.get_deployment_roles_by_collection(collection_data, server_interface, view)
                dep_roles = [dep_role for dep_role in dep_roles if dep_role.get('roleType') == role_type]
                if self.action != Actions.ADD_SERVERS and not dep_roles:
                    role.update({
                        'status': Status.UNAVAILABLE,
                        'message': 'Role not found'
                    })
                    result.append(self.make_validate_result(role, role))
                    continue
                deployment_role = dep_roles[0] if self.action != Actions.ADD_SERVERS else {}
            except Exception as e:
                g.user.logger.warning(
                    'Failed to get role data: {}'.format(str(e)))
                role.update({
                    'status': Status.UNAVAILABLE,
                    'message': str(e)
                })
                result.append(self.make_validate_result(role, role))
                continue

            role_validation = dict()
            if self.action in (Actions.MOVE, Actions.COPY):
                if target[0].get('type') in (
                        EntityV2.ZONE, EntityV2.IP4_BLOCK, EntityV2.IP4_NETWORK, EntityV2.IP6_BLOCK,
                        EntityV2.IP6_NETWORK):
                    for single_target in target:
                        role_validation = self.validate_copy_move_actions(copy.deepcopy(deployment_role),
                                                                          target=single_target)
                        result.append(self.make_validate_result(role, role_validation, single_target))
                else:
                    if self.action == Actions.COPY:
                        collection_duplicate_validation = self.validate_duplicate_collection_roles(check_role=role,
                                                                                                   role_list=roles)
                        if collection_duplicate_validation.get('status') == Status.DUPLICATED:
                            role.update({
                                'status': collection_duplicate_validation.get('status'),
                                'message': collection_duplicate_validation.get('message')
                            })
                            result.append(self.make_validate_result(role, collection_duplicate_validation, target[0]))
                            continue
                    role_validation = self.validate_copy_move_actions(deployment_role, target=target[0])
                    result.append(self.make_validate_result(role, role_validation, target[0]))
            elif self.action == Actions.MOVE_PRIMARY:
                role_validation = self.validate_move_primary(deployment_role, target=target[0])
                result.append(self.make_validate_result(role, role_validation, target[0]))
            elif self.action == Actions.ADD_SERVERS:
                for interface in target:
                    new_role = copy.deepcopy(role)
                    if not interface.get('role_type'):
                        raise InvalidParam("Missing role_type for add server roles action")
                    new_role.update({
                        'server_interface': interface.get('name'),
                        'role_type': interface.get('role_type'),
                        'view': role.get('view', interface.get('view')),
                        'configuration': configuration,
                        'zone_transfer_interface': interface.get('zone_transfer_interface'),
                    })

                    role_validation = self.validate_add_servers(new_role, collection_data)
                    result.append(self.make_validate_result(new_role, role_validation, collection_data))
            elif self.action in [Actions.HIDE, Actions.EXPOSE]:
                role_validation = self.validate_hide_expose_actions(deployment_role)

                result.append(self.make_validate_result(role, role_validation, target))
            elif self.action == Actions.DELETE:
                role_validation = self.validate_delete_actions(deployment_role)

                result.append(self.make_validate_result(role, role_validation, target))
        return result

    def make_validate_result(self, role, role_validation, target=None):
        role_collection = role.get('collection')
        role_type = role.get('role_type')
        role_server_interface = role.get('server_interface', '')
        role_view = role.get('view', '')
        target_type = target.get('type') if target else ''
        target_role_collection = role_collection if self.action != Actions.ADD_SERVERS else target.get('collection')
        is_server_relevant_action = self.action in (Actions.HIDE, Actions.EXPOSE, Actions.MOVE,
                                                    Actions.MOVE_PRIMARY) \
                                    or (self.action == Actions.COPY
                                        and target_type not in (
                                            EntityV2.ZONE, EntityV2.IP4_BLOCK, EntityV2.IP6_BLOCK, EntityV2.IP6_NETWORK,
                                            EntityV2.IP4_NETWORK))
        if not is_server_relevant_action:
            if target_type in (EntityV2.IP6_BLOCK, EntityV2.IP4_BLOCK):
                target_role_collection = Collections.BLOCKS
            elif target_type in (EntityV2.IP4_NETWORK, EntityV2.IP6_NETWORK):
                target_role_collection = Collections.NETWORKS
            else:
                target_role_collection = Collections.ZONES
        role_dictionary = {
            'collection': role_collection,
            'server_interface': role_server_interface,
            'role_type': role_type,
            'view': role_view,
        }
        new_role_dictionary = {
            'collection': target_role_collection,
            'role_type': role_validation.get('target_role_type', role_type),
            'server_interface': target.get('name') if is_server_relevant_action and target else role_server_interface,
            'view': target.get('view') if target and target.get(
                'view') and self.action != Actions.ADD_SERVERS else role_view,
        }

        if role_collection == Collections.ZONES:
            absolute_name = role.get('absolute_name', '')
            role_dictionary['absolute_name'] = absolute_name
            if is_server_relevant_action:
                new_role_dictionary['absolute_name'] = absolute_name
        elif role_collection in (Collections.NETWORKS, Collections.BLOCKS):
            _range = role.get('range', '')
            role_dictionary.update({
                'range': _range,
                'reverse_zone': get_reverse_zone_name(_range)
            })
            if is_server_relevant_action:
                new_role_dictionary.update({
                    'range': _range,
                    'reverse_zone': get_reverse_zone_name(_range)
                })
        elif role_collection:
            name = role.get('name', '')
            role_dictionary['name'] = name
            if is_server_relevant_action:
                new_role_dictionary['name'] = name

        if not is_server_relevant_action and target_type == EntityV2.ZONE:
            new_role_dictionary['absolute_name'] = target.get('absoluteName')
            if self.action == Actions.ADD_SERVERS:
                role_dictionary.update({
                    'absolute_name': target.get('absoluteName'),
                    'collection': target_role_collection,
                })
        elif not is_server_relevant_action and target_type in (EntityV2.IP4_NETWORK, EntityV2.IP6_NETWORK,
                                                               EntityV2.IP4_BLOCK, EntityV2.IP6_BLOCK):
            new_role_dictionary.update({
                'range': target.get('range'),
                'reverse_zone': get_reverse_zone_name(target.get('range')),
            })
            if self.action == Actions.ADD_SERVERS:
                new_role_dictionary['view'] = role_view
                role_dictionary.update({
                    'range': target.get('range'),
                    'reverse_zone': get_reverse_zone_name(target.get('range')),
                    'collection': target_role_collection,
                    'view': role_view
                })

        validate_result = {
            'status': role_validation.get('status', Status.AVAILABLE),
            'message': role_validation.get('message', ''),
            'role': role_dictionary,
            'new_role': new_role_dictionary
        }
        return validate_result


def remove_none_from_dict(original):
    return {k: v for k, v in original.items() if v is not None}
