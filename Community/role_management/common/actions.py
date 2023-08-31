# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
import copy

from flask import g

from bluecat.entity import Entity

from .common import get_collection_name
from .options import validate_existing_dns_options
from .exception import (
    ActionConflictException,
    InvalidDNSOptionException,
    InvalidZoneTransferInterfaceException,
    InvalidParam
)
from .roles import (
    get_merge_role_result,
    create_deployment_role_object,
    get_duplicate_role_by_server,
    get_duplicate_role_in_zone,
    validate_valid_zone_transfer_and_target_interface, to_display_rt
)
from .constants import Status
from .roles import convert_primary_role

from ..rest_v2 import common
from ..rest_v2.constants import (
    RoleType,
    HIDE_ROLES,
    EXPOSE_ROLES,
    Collections,
    EntityV2,
    PRIMARY_GROUP,
    Actions,
    enable_copy_dns_option
)


class RoleAction:
    def __init__(self, action, validate=False):
        self.action = action
        self.validate = validate
        self.collection = None
        if action == Actions.COPY:
            self.zone_option_dict = dict()

    def set_role_collection(self, collection):
        self.collection = collection

    def validate_and_copy_role_to_server(self, role, new_server_interface_id):
        """
        Validate duplicated roles in new server interface, copy and merge roles if roles are compatible
        :param role: role object to be copied
        :param new_server_interface_id: new server interface id
        :return: status of copy role to server action
        """
        try:
            role = copy.deepcopy(role)
            if role.get('_inheritedFrom'):
                result = {
                    "roleType": role.get('roleType'),
                    "message": "Skip copying role to server since the role is inherited from another role",
                    "status": Status.INFO,
                    "targetRoleType": ''
                }
                return result
            if role.get('serverInterface').get('id') == new_server_interface_id:
                result = {
                    "roleType": role.get('roleType'),
                    "message": "Ignored, cannot copy role {} to same server interface named {}.".format(
                        to_display_rt(role.get('roleType')), role.get('serverInterface').get('name')),
                    "status": Status.INFO,
                    "targetRoleType": ''
                }
                return result
            if not validate_valid_zone_transfer_and_target_interface(role, new_server_interface_id):
                result = {
                    "roleType": role.get('roleType'),
                    "message": "Ignored, cannot copy role to same server interface with zone transfer.",
                    "status": Status.INFO,
                    "targetRoleType": ''
                }
                return result
            duplicate_role = get_duplicate_role_by_server(current_role=role, interface_id=new_server_interface_id,
                                                          collection=self.collection)
            if duplicate_role:
                result = self.merge_copy_move_role_to_server(duplicated_role=duplicate_role, current_role=role)
            else:
                result = self.copy_role_to_server(role=role, new_server_interface_id=new_server_interface_id)
        except Exception as e:
            g.user.logger.error(f"Copied role to server action exception: {e}")
            result = {
                "roleType": role.get('roleType'),
                "message": "Failed to copy role: {}".format(str(e)),
                "status": Status.FAILED
            }
        return result

    def validate_and_copy_role_to_zone(self, role, new_zone, option_filter=None):
        """
        Validate duplicated roles in new zone, copy and merge roles if roles are compatible
        :param role: role object to be copied
        :param new_zone: new zone or reversed zone object
        :param option_filter: filter which option will be copied
        :return: status of copy role to zone action
        """
        try:
            rest_v2 = g.user.v2
            role = rest_v2.get_deployment_role(role.get('id'))
            if_id = role.get('serverInterface').get('id')
            roles_of_zone = rest_v2.get_deployment_roles_by_collection(
                EntityV2.get_collection(new_zone.get('type')), new_zone.get('id')).get('data')
            for target_role in roles_of_zone:
                if target_role.get('_inheritedFrom'):
                    break
                target_role_type = target_role.get('roleType')
                if target_role.get('roleType') in PRIMARY_GROUP and role.get(
                        'roleType') in PRIMARY_GROUP and target_role.get('serverInterface').get('id') != if_id:
                    return {
                        "roleType": role.get('roleType'),
                        "message": "Ignored, {} role already exists".format(to_display_rt(target_role_type)),
                        "status": Status.INFO,
                        "targetRoleType": ''
                    }
            if enable_copy_dns_option:
                zone_options = None
                if self.zone_option_dict.get(new_zone.get('id')) is not None:
                    zone_options = self.zone_option_dict.get(new_zone.get('id'))
                options = validate_existing_dns_options(role, new_zone, self.collection, zone_options, option_filter)
                if isinstance(options, dict) and options.get('option_name'):
                    conflicted_option_name = options.get('option_name')
                    zone_type = options.get('zone_type')
                    zone_name = options.get('zone_name')
                    raise InvalidDNSOptionException('DNS Option {} already exists in {} {}'.format(conflicted_option_name,
                                                                                                   zone_type,
                                                                                                   zone_name))
                zone_id = new_zone.get('id')
                if self.zone_option_dict.get(zone_id) is None:
                    self.zone_option_dict[zone_id] = rest_v2.get_deployment_option_by_collection(
                        EntityV2.get_collection(new_zone.get('type')), new_zone.get('id'),
                        fields='id, name, type, _inheritedFrom, definition, serverScope').get('data')
                self.copy_options_to_collection(new_zone, options)

            duplicate_role = get_duplicate_role_in_zone(new_zone=new_zone,
                                                        interface_id=role.get('serverInterface').get('id'))
            if duplicate_role:
                result = self.merge_copy_role_to_zone(role=duplicate_role, current_role=role)
            else:
                result = self.copy_role_to_zone(role=role, new_zone=new_zone)
        except InvalidDNSOptionException as option_exception:
            g.user.logger.error(f"{option_exception}")
            result = {
                "roleType": role.get('roleType'),
                "message": str(option_exception),
                "status": Status.CONFLICTED
            }
        except Exception as e:
            g.user.logger.error(f"Copied role to server action exception: {e}")
            result = {
                "roleType": role.get('roleType'),
                "message": "Failed to copy role: {}".format(str(e)),
                "status": Status.FAILED
            }
        return result

    def validate_and_move_role_to_server(self, role, new_server_interface_id):
        """
        Validate duplicated roles in new server interface, move and merge roles if roles are compatible
        :param role: role object to be moved
        :param new_server_interface_id: new server interface id
        :return: status of move role to server action
        """
        try:
            role = copy.deepcopy(role)
            if role.get('_inheritedFrom'):
                result = {
                    "roleType": role.get('roleType'),
                    "message": "Skip moving role to server since the role is inherited from another role",
                    "status": Status.INFO,
                    "targetRoleType": ''
                }
                return result
            if role.get('serverInterface').get('id') == new_server_interface_id and not role.get('_inheritedFrom'):
                result = {
                    "roleType": role.get('roleType'),
                    "message": "Ignored, cannot move role to same server interface.",
                    "status": Status.INFO,
                    "targetRoleType": ''
                }
                return result
            if not validate_valid_zone_transfer_and_target_interface(role, new_server_interface_id):
                result = {
                    "roleType": role.get('roleType'),
                    "message": "Ignored, cannot move role to same server interface with zone transfer.",
                    "status": Status.INFO,
                    "targetRoleType": ''
                }
                return result
            duplicate_role = get_duplicate_role_by_server(current_role=role, interface_id=new_server_interface_id,
                                                          collection=self.collection)
            if duplicate_role:
                result = self.merge_copy_move_role_to_server(current_role=role, duplicated_role=duplicate_role)
            else:
                result = self.move_role_to_server(role=role, new_server_interface_id=new_server_interface_id)
        except Exception as e:
            g.user.logger.error(f"Moving role to server action exception: {e}")
            result = {
                "roleType": role.get('roleType'),
                "message": "Failed to move role: {}".format(str(e)),
                "status": Status.FAILED
            }
        return result

    def validate_and_move_primary_role(self, role, new_server_interface_id):
        """
        Validate duplicated roles in new server interface, move and modify roles if roles are compatible
        :param role: primary role object to be moved
        :param new_server_interface_id: new server interface id

        :return: status of copy role to zone action
        """
        try:
            rest_v2 = g.user.v2
            role = copy.deepcopy(role)
            server_interface_name = rest_v2.get_interface(new_server_interface_id).get('name')
            collection_id = self.collection.get('id')
            collection = EntityV2.get_collection(self.collection.get('type'))
            roles_of_collection = rest_v2.get_deployment_roles_by_collection(collection, collection_id).get('data')
            roles_of_collection = [] if roles_of_collection and roles_of_collection[0].get('_inheritedFrom') \
                else roles_of_collection
            duplicate_role = get_duplicate_role_by_server(current_role=role, interface_id=new_server_interface_id,
                                                          collection=self.collection)
            # The old Primary server becomes a Secondary, Hidden Primary becomes a Stealth Secondary.
            for role in roles_of_collection:
                if role.get('roleType') == RoleType.PRIMARY:
                    self.update_role_type(role_id=role.get('id'), new_role_type=RoleType.SECONDARY)
                if role.get('roleType') == RoleType.HIDDEN_PRIMARY:
                    self.update_role_type(role_id=role.get('id'), new_role_type=RoleType.STEALTH_SECONDARY)

            role_type = RoleType.HIDDEN_PRIMARY
            if duplicate_role:
                dup_role_type = duplicate_role.get('roleType')
                if dup_role_type in (RoleType.SECONDARY, RoleType.PRIMARY):
                    self.update_role_type(role_id=duplicate_role.get('id'), new_role_type=RoleType.PRIMARY)
                    role_type = ''
                elif dup_role_type in (RoleType.STUB, RoleType.FORWARDER):
                    return {
                        "message": "Conflicted with recursive role, cannot move primary role to server {}".format(
                            server_interface_name)
                    }
            if role_type:
                role.update({
                    "type": Entity.DeploymentRole,
                    "roleType": role_type,
                    "serverInterface": {
                        "id": new_server_interface_id
                    }
                })
                if duplicate_role:
                    self.update_role_type(role_id=duplicate_role.get('id'), new_role_type=RoleType.HIDDEN_PRIMARY)
                else:
                    rest_v2.add_dns_deployment_role(role=role, collection=collection, collection_id=collection_id)
            return {
                "roleType": role.get('roleType'),
                "message": "Successfully moved primary to server {}".format(server_interface_name),
                "status": Status.SUCCESSFULLY,
                "targetRoleType": RoleType.HIDDEN_PRIMARY if role_type else RoleType.PRIMARY
            }
        except Exception as e:
            g.user.logger.error(f"Moved primary role to server action exception: {e}")
            result = {
                "roleType": role.get('roleType'),
                "message": "Failed to move primary role: {}".format(str(e)),
                "status": Status.FAILED
            }
        return result

    def add_servers(self, role, collection):
        """
        Validate duplicated roles in new server interface, copy and merge roles if roles are compatible
        :param role: role object to be added (SECONDARY, STEALTH_SECONDARY, FORWARDING, STUB)
        :param collection: collection zone to add server roles
        :return: status of add server action
        """
        try:

            role_type = role.get('roleType')
            if role_type.upper() not in (
                    RoleType.STEALTH_SECONDARY, RoleType.SECONDARY, RoleType.FORWARDER, RoleType.STUB):
                return {
                    "roleType": role_type.upper(),
                    "message": "Ignored, role type {} is not allowed".format(to_display_rt(role_type)),
                    "status": Status.INFO
                }
            role = create_deployment_role_object(role_type=role.get('roleType'),
                                                 configuration_cls=role.get('configuration'),
                                                 view_name=role.get('view'),
                                                 server_interface=role.get('server_interface'),
                                                 zone_transfer_interface=role.get('zone_transfer_interface'))

            server_interface_id = role.get('serverInterface').get('id')
            duplicate_role = get_duplicate_role_in_zone(new_zone=collection, interface_id=server_interface_id)
            if duplicate_role:
                result = self.merge_copy_role_to_zone(role=duplicate_role, current_role=role)
            else:
                result = self.copy_role_to_zone(role=role, new_zone=collection)
        except InvalidZoneTransferInterfaceException as e:
            g.user.logger.error(str(e))
            result = {
                "roleType": role.get('roleType'),
                "message": "{}".format(str(e)),
                "status": Status.CONFLICTED
            }
        except Exception as e:
            g.user.logger.error(f"Added server exception: {e}")
            result = {
                "roleType": role.get('roleType'),
                "message": "Failed to copy role: {}".format(str(e)),
                "status": Status.FAILED
            }
        return result

    def copy_role_to_server(self, role, new_server_interface_id):
        """
        Copy role to new server interface
        :param role: role object to me copied
        :param new_server_interface_id: new server interface id
        :return: status of copy role to server
        """
        rest_v2 = g.user.v2
        role_type = role.get('roleType')
        server_interface_dict = {
            'id': new_server_interface_id
        }
        server_interface_name = rest_v2.get_interface(new_server_interface_id).get('name')
        try:
            role = convert_primary_role(role)
            collection = self.collection
            collection_type = EntityV2.get_collection(collection.get('type'))
            collection_id = collection.get('id')
            role['serverInterface'] = server_interface_dict
            rest_v2.add_dns_deployment_role(role=role, collection=collection_type,
                                            collection_id=collection_id)
            result = {
                "roleType": role_type,
                "message": "Successfully copied role {} to server {}".format(to_display_rt(role_type),
                                                                             server_interface_name),
                "status": Status.SUCCESSFULLY,
                "targetRoleType": role.get('roleType')
            }
        except Exception as e:
            g.user.logger.error(f"Copied role to server exception: {e}")
            result = {
                "roleType": role_type,
                "message": "Failed to copy role {} to server {}: {}".format(to_display_rt(role_type),
                                                                            server_interface_name, str(e)),
                "status": Status.FAILED
            }
        return result

    def copy_role_to_zone(self, role, new_zone):
        """
        Copy role to a new zone (View/Zone) or reverse zone (IPBlock, IPNetwork)
        :param role: role object to me copied
        :param new_zone: new zone id
        :return: status of copy role to zone
        """
        role_type = role.get('roleType')
        new_zone_name = 'absoluteName'
        rest_v2 = g.user.v2
        try:
            new_zone_type = new_zone.get('type')
            rest_v2.add_dns_deployment_role(role=role,
                                            collection=EntityV2.get_collection(new_zone_type),
                                            collection_id=new_zone.get('id'))
            if EntityV2.get_collection(new_zone_type) in [Collections.BLOCKS, Collections.NETWORKS]:
                new_zone_name = 'range'
            new_zone_name = "{} {}".format(new_zone_type, new_zone.get(new_zone_name))
            result = {
                "roleType": role_type,
                "message": "Successfully added role {} to {}".format(to_display_rt(role_type), new_zone_name),
                "status": Status.SUCCESSFULLY,
                "targetRoleType": role_type
            }
        except Exception as e:
            g.user.logger.error(f"Copied role to server exception: {e}")
            result = {
                "roleType": role_type,
                "message": "Failed to copy role {} to zone {}: {}".format(to_display_rt(role_type),
                                                                          new_zone.get(new_zone_name),
                                                                          str(e)),
                "status": Status.FAILED
            }
        return result

    def move_role_to_server(self, role, new_server_interface_id):
        """
        Move role to new server interface
        :param role: role object to me moved
        :param new_server_interface_id: new server interface id
        :return: status of move role to server
        """
        role_type = role.get('roleType')
        server_interface_dict = {
            'id': new_server_interface_id
        }
        rest_v2 = g.user.v2
        server_interface_name = rest_v2.get_interface(new_server_interface_id).get('name')
        try:
            collection = common.get_parent_entity_of_role(role)
            role['serverInterface'] = server_interface_dict
            if role_type == RoleType.HIDDEN_PRIMARY:
                role_type = RoleType.STEALTH_SECONDARY
                role['roleType'] = role_type
            if role.get('_inheritedFrom'):
                collection_type = EntityV2.get_collection(self.collection.get('type'))
                collection_id = self.collection.get('id')
            else:
                rest_v2.delete_deployment_role(role.get('id'))
                collection_type = collection.get('type')
                collection_id = collection.get('id')
            rest_v2.add_dns_deployment_role(role=role, collection=collection_type,
                                            collection_id=collection_id)
            result = {
                "roleType": role_type,
                "message": "Successfully moved role {} to server {}".format(to_display_rt(role_type),
                                                                            server_interface_name),
                "status": Status.SUCCESSFULLY,
                "targetRoleType": role_type
            }
        except Exception as e:
            g.user.logger.error(f"Moved role to server exception: {e}")
            result = {
                "roleType": role_type,
                "message": "Failed to move role {} to server {}: {}".format(to_display_rt(role_type),
                                                                            server_interface_name, str(e)),
                "status": Status.FAILED
            }
        return result

    def update_role_server(self, role_id, new_server_interface_id):
        """
        Update server interface of DNS Deployment Role
        :param role_id: ID of role to be updated
        :param new_server_interface_id: new server interface id
        :return: new DNS Deployment Role object
        """
        try:
            rest_v2 = g.user.v2
            role = rest_v2.get_deployment_role(role_id)
            server_interface = {
                'id': new_server_interface_id
            }
            role['serverInterface'] = server_interface
            result = rest_v2.update_dns_deployment_role(role=role, role_id=role_id)
            return result
        except Exception as e:
            g.user.logger.error(f"Update server of role exception: {e}")

    def update_role_type(self, role_id, new_role_type):
        """
        Update role type of DNS Deployment Role
        :param role_id: ID of role to be updated
        :param new_role_type: new role type
        :return: new DNS Deployment Role object
        """
        try:
            rest_v2 = g.user.v2
            role = rest_v2.get_deployment_role(role_id)
            if new_role_type not in RoleType.all():
                g.user.logger.error("Invalid role type {}".format(new_role_type))
                raise InvalidParam("Invalid role type")
            role['roleType'] = new_role_type
            result = rest_v2.update_dns_deployment_role(role=role, role_id=role_id)
            return result
        except Exception as e:
            g.user.logger.error(f"Update role type exception: {e}")
            raise e

    def merge_copy_role(self, role, current_role):
        """
        Merge copied role with duplicated role in same server
        according to this hierarchy:
        Stealth Secondary → Secondary → Primary
        Stealth Secondary → Hidden Primary → Primary
        :param role: duplicated role in same server
        :param current_role: copied role
        :return: status of merge roles function
        """
        current_role_type = current_role.get('roleType')
        role_type = role.get('roleType')
        try:
            result = {}
            if role_type == RoleType.STEALTH_SECONDARY:
                if current_role_type in (RoleType.PRIMARY, RoleType.SECONDARY):
                    self.update_role_type(role_id=role.get('id'), new_role_type=RoleType.SECONDARY)
                    result = generate_merged_result(current_role_type, role_type, RoleType.SECONDARY)
                elif current_role_type == RoleType.HIDDEN_PRIMARY:
                    result = generate_merged_result(current_role_type, role_type, RoleType.STEALTH_SECONDARY)
            elif role_type == RoleType.HIDDEN_PRIMARY:
                if current_role_type == RoleType.SECONDARY:
                    self.update_role_type(role_id=role.get('id'), new_role_type=RoleType.PRIMARY)
                    result = generate_merged_result(current_role_type, role_type, RoleType.PRIMARY)
                elif current_role_type in (RoleType.STEALTH_SECONDARY, RoleType.PRIMARY):
                    result = generate_merged_result(current_role_type, role_type, RoleType.HIDDEN_PRIMARY)
            elif role_type == RoleType.SECONDARY:
                if current_role_type in (RoleType.PRIMARY, RoleType.HIDDEN_PRIMARY, RoleType.STEALTH_SECONDARY):
                    result = generate_merged_result(current_role_type, role_type, RoleType.SECONDARY)
            elif role_type == RoleType.PRIMARY and current_role_type in (RoleType.HIDDEN_PRIMARY,
                                                                         RoleType.SECONDARY,
                                                                         RoleType.STEALTH_SECONDARY):
                result = generate_merged_result(current_role_type, role_type, RoleType.SECONDARY)

            if not result:
                result = {
                    "roleType": current_role_type,
                    "message": "Conflicted. Cannot merge role {} with {}".format(to_display_rt(current_role_type),
                                                                                 to_display_rt(role_type)),
                    "status": Status.CONFLICTED,
                    "targetRoleType": ''
                }
        except Exception as e:
            g.user.logger.error(f"Merge role of exception: {e}")
            result = {
                "roleType": current_role_type,
                "message": "Conflicted. Failed to merge role {} with {}: {}".format(to_display_rt(current_role_type),
                                                                                    to_display_rt(role_type),
                                                                                    str(e)),
                "status": Status.CONFLICTED,
                "targetRoleType": ''
            }
        return result

    def merge_copy_move_role_to_server(self, current_role, duplicated_role):
        """
        Merge moved role with duplicated role in same server
        according to this hierarchy:
        Stealth Secondary → Secondary → Primary
        Stealth Secondary → Hidden Primary → Primary
        :param duplicated_role: duplicated role in same server
        :param current_role: copied role
        :return: status of merge roles function
        """
        current_role_type = current_role.get('roleType')
        duplicated_role_type = duplicated_role.get('roleType')
        try:
            rest_v2 = g.user.v2
            if duplicated_role_type == current_role_type:
                return {
                    "roleType": current_role_type,
                    "message": "Ignored, role {} already exists".format(current_role_type),
                    "status": Status.INFO,
                    "targetRoleType": ''
                }
            if self.action == Actions.COPY:
                current_role = convert_primary_role(current_role)
            elif current_role_type == RoleType.HIDDEN_PRIMARY:
                current_role['roleType'] = RoleType.STEALTH_SECONDARY

            current_role_type = current_role.get('roleType')
            merged_role_type = get_merge_role_result(current_role_type, duplicated_role_type)
            if self.action == Actions.MOVE:
                rest_v2.delete_deployment_role(current_role.get('id'))
            if duplicated_role_type != merged_role_type:
                self.update_role_type(role_id=duplicated_role.get('id'), new_role_type=merged_role_type)
            result = generate_merged_result(current_role_type, duplicated_role_type, merged_role_type)
        except ActionConflictException as e:
            g.user.logger.error(str(e))
            result = {
                "roleType": current_role_type,
                "message": "Conflicted. Cannot merge role {} with {}".format(to_display_rt(current_role_type),
                                                                             to_display_rt(duplicated_role_type)),
                "status": Status.CONFLICTED,
                "targetRoleType": ''
            }
        except Exception as e:
            g.user.logger.error(f"Merge role of exception: {e}")
            result = {
                "roleType": current_role_type,
                "message": "Conflicted. Failed to merge role {} with {}: {}".format(to_display_rt(current_role_type),
                                                                                    to_display_rt(duplicated_role_type),
                                                                                    str(e)),
                "status": Status.CONFLICTED,
                "targetRoleType": ''
            }
        return result

    def merge_copy_role_to_zone(self, role, current_role):
        """
        Merge copied role with duplicated role in same collection
        according to this hierarchy:
        Stealth Secondary → Secondary → Primary
        Stealth Secondary → Hidden Primary → Primary
        :param role: duplicated role in same collection
        :param current_role: copied role
        :return: status of merge roles function
        """
        current_role_type = current_role.get('roleType')
        role_type = role.get('roleType')
        try:
            result = {}
            if role_type == current_role_type:
                return {
                    "roleType": current_role_type,
                    "message": "Ignored, role {} already exists".format(to_display_rt(current_role_type)),
                    "status": Status.INFO,
                    "targetRoleType": ''
                }
            elif role_type == RoleType.STEALTH_SECONDARY:
                if current_role_type in (RoleType.PRIMARY, RoleType.SECONDARY, RoleType.HIDDEN_PRIMARY):
                    self.update_role_type(role_id=role.get('id'), new_role_type=current_role_type)
                    result = generate_merged_result(current_role_type, role_type, current_role_type)
            elif role_type == RoleType.HIDDEN_PRIMARY:
                if current_role_type in EXPOSE_ROLES:
                    self.update_role_type(role_id=role.get('id'), new_role_type=RoleType.PRIMARY)
                    result = generate_merged_result(current_role_type, role_type, RoleType.PRIMARY)
                elif current_role_type == RoleType.STEALTH_SECONDARY:
                    result = generate_merged_result(current_role_type, role_type, RoleType.HIDDEN_PRIMARY)
            elif role_type == RoleType.SECONDARY:
                if current_role_type in PRIMARY_GROUP:
                    self.update_role_type(role_id=role.get('id'), new_role_type=RoleType.PRIMARY)
                    result = generate_merged_result(current_role_type, role_type, RoleType.PRIMARY)
                elif current_role_type == RoleType.STEALTH_SECONDARY:
                    result = generate_merged_result(current_role_type, role_type, RoleType.SECONDARY)
            elif role_type == RoleType.PRIMARY:
                result = generate_merged_result(current_role_type, role_type, RoleType.PRIMARY)

            if not result:
                result = {
                    "roleType": current_role_type,
                    "message": "Conflicted. Cannot merge role {} with {}".format(to_display_rt(current_role_type),
                                                                                 to_display_rt(role_type)),
                    "status": Status.CONFLICTED,
                    "targetRoleType": ''
                }
        except Exception as e:
            g.user.logger.error(f"Merged role of exception: {e}")
            result = {
                "roleType": current_role_type,
                "message": "Conflicted. Failed to merge role {} with {}: {}".format(to_display_rt(current_role_type),
                                                                                    to_display_rt(role_type),
                                                                                    str(e)),
                "status": Status.CONFLICTED,
                "targetRoleType": ''
            }
        return result

    def expose_roles(self, roles):
        result = []
        rest_v2 = g.user.v2
        origin_role_ids = {role.get('id') for role in roles if not role.get('_inheritedFrom')}
        for role in roles:
            role_type = role.get('roleType')
            target_role = RoleType.PRIMARY if role_type == RoleType.HIDDEN_PRIMARY else RoleType.SECONDARY
            status = Status.SUCCESSFULLY
            message = 'Successfully made visible role {} to {}'.format(to_display_rt(role_type),
                                                                       to_display_rt(target_role))
            try:
                is_actionable_inherited_role = role.get('_inheritedFrom') and role.get('id') in origin_role_ids
                if is_actionable_inherited_role:
                    g.user.logger.warning(get_warning_inherited_roles_message(role))
                elif role.get('_inheritedFrom'):
                    status = Status.FAILED
                    message = "Cannot make visible for inherited role"
                elif role_type not in HIDE_ROLES:
                    status = Status.INFO
                    message = "{} role is hidden.".format(to_display_rt(role_type))
                else:
                    role['roleType'] = target_role
                    rest_v2.update_dns_deployment_role(role.get('id'), role)
            except Exception as e:
                status = 'Failed to make visible role {} to {}: {}'.format(to_display_rt(role_type),
                                                                           to_display_rt(target_role), str(e))
                if '409' in str(e):
                    status = Status.CONFLICTED
                    message = "{} role is hidden.".format(to_display_rt(role_type))
            result.append({
                'roleType': role_type,
                'targetRoleType': target_role,
                'status': status,
                'message': message
            })
        return result

    def hide_roles(self, roles):
        result = []
        origin_role_ids = {role.get('id') for role in roles if not role.get('_inheritedFrom')}
        rest_v2 = g.user.v2
        for role in roles:
            role_type = role.get('roleType')
            target_role = RoleType.STEALTH_SECONDARY if role_type == RoleType.SECONDARY else RoleType.HIDDEN_PRIMARY
            status = Status.SUCCESSFULLY
            message = 'Successfully hidden role {} to {}'.format(to_display_rt(role_type), to_display_rt(target_role))
            try:
                is_actionable_inherited_role = role.get('_inheritedFrom') and role.get('id') in origin_role_ids
                if is_actionable_inherited_role:
                    g.user.logger.warning(get_warning_inherited_roles_message(role))
                elif role.get('_inheritedFrom'):
                    status = Status.FAILED
                    message = "Cannot make visible for inherited role"
                elif role_type not in EXPOSE_ROLES:
                    status = Status.INFO
                    message = "{} role is hidden.".format(to_display_rt(role_type))
                else:
                    role['roleType'] = target_role
                    rest_v2.update_dns_deployment_role(role.get('id'), role)
            except Exception as e:
                status = Status.FAILED
                message = "Failed to hide role {} to {}: {}".format(to_display_rt(role_type),
                                                                    to_display_rt(target_role), str(e))
                if '409' in str(e):
                    status = Status.CONFLICTED
                    message = "{} role is hidden.".format(to_display_rt(role_type))
            result.append({
                'roleType': role_type,
                'targetRoleType': target_role,
                'status': status,
                'message': message
            })
        return result

    def copy_options_to_collection(self, target_zone, options):
        rest_v2 = g.user.v2
        collection_id = target_zone.get('id')
        collection = EntityV2.get_collection(target_zone.get('type'))
        for option in options:
            try:
                rest_v2.add_deployment_option(collection, collection_id, option)
            except Exception as e:
                display_name = common.get_display_option_name(option)
                zone_type = target_zone.get('type')
                zone_name = target_zone.get('range') \
                    if zone_type in (EntityV2.IP4_NETWORK, EntityV2.IP6_NETWORK, EntityV2.IP6_BLOCK, EntityV2.IP4_BLOCK) \
                    else target_zone.get('absoluteName', target_zone.get('name'))
                g.user.logger.error(
                    'Unable to add option {} to {} {}: {}'.format(display_name, zone_type, zone_name, str(e)))

    def delete_roles(self, roles):
        result = []
        rest_v2 = g.user.v2
        origin_role_ids = {role.get('id') for role in roles if not role.get('_inheritedFrom')}
        for role in roles:
            role_type = role.get('roleType')
            status = Status.SUCCESSFULLY
            message = 'Successfully deleted role {}'.format(to_display_rt(role_type))
            try:
                is_actionable_inherited_role = role.get('_inheritedFrom') and role.get('id') in origin_role_ids
                if is_actionable_inherited_role:
                    g.user.logger.warning(get_warning_inherited_roles_message(role, is_deleted=True))
                elif role.get('_inheritedFrom'):
                    status = Status.FAILED
                    message = 'Cannot delete inherited role'
                else:
                    rest_v2.delete_deployment_role(role.get('id'))
            except Exception as e:
                status = Status.FAILED
                message = "Failed to delete role {}: {}".format(to_display_rt(role_type), str(e))
            result.append({
                'roleType': role_type,
                'targetRoleType': role_type,
                'status': status,
                'message': message
            })
        return result


def generate_merged_result(current_role_type, duplicated_role_type, final_role_type):
    return {
        "roleType": current_role_type,
        "message": "Successfully merged role {} with {} into {}".format(to_display_rt(current_role_type),
                                                                        to_display_rt(duplicated_role_type),
                                                                        to_display_rt(final_role_type)),
        "status": Status.SUCCESSFULLY,
        "targetRoleType": final_role_type
    }


def get_warning_inherited_roles_message(role, is_deleted=False):
    role_type = role.get('roleType')
    inherited_collection = role.get('collection')
    inherited_coll_type = inherited_collection.get('type')
    inherited_coll_name = get_collection_name(inherited_collection)
    origin_id = common.get_parent_entity_of_role(role).get('id')
    origin_collection = g.user.v2.get_entity_by_id(origin_id)
    origin_coll_type = origin_collection.get('type')
    origin_coll_name = get_collection_name(origin_collection)
    action = 'deleted' if is_deleted else 'modified'
    return 'WARNING: Origin {} Role ({} {}) of Inherited Role ({} {}) will also be {}' \
        .format(to_display_rt(role_type), inherited_coll_type, inherited_coll_name, origin_coll_type, origin_coll_name,
                action)
