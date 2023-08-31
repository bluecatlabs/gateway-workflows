# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates\
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from flask import g

from bluecat.entity import Entity

from .common import get_config
from .exception import ActionConflictException
from .roles import (
    convert_primary_role,
    get_merge_role_result,
    create_deployment_role_object,
    get_duplicate_role_by_server,
    get_duplicate_role_in_zone, validate_valid_zone_transfer_and_target_interface
)
from .constants import (
    OpType,
    MIGRATION_PATH,
    MIGRATION_CONFIG,
    OnExist,
    DNSDeploymentRoles,
    MAX_FILE_STORE
)

from ..rest_v2 import common
from ..rest_v2.constants import (
    EntityV2,
    Actions,
    RoleType,
    ZoneType,
    PRIMARY_GROUP,
    DEFAULT_FIELDS,
    EXPOSE_ROLES
)

DOCTYPE_QUALIFIED_NAME = 'data'
DOCTYPE_PUBLIC_ID = "-//BlueCat Networks//Proteus Migration Specification 9.3-alt//EN"
DOCTYPE_SYSTEM_ID = "http://www.bluecatnetworks.com/proteus-migration-9.3-alt.dtd"
DEFAULT_XML_OUTPUT_NAME = 'migration.xml'


def group_role_by_parent_id(cls_data, action, roles, configuration_name='', view_name='', des_roles=None):
    rest_v2 = g.user.v2

    def update_f_roles(cls, role_rs, filter_roles, is_delete_role=False):
        if role_rs:
            if is_delete_role:
                # TODO
                role_rs['on-exist'] = 'delete-tree'
            cls_id = cls.get('id')
            if filter_roles.get(cls_id):
                filter_roles[cls_id]['roles'].append(role_rs)
            else:
                filter_roles[cls_id] = {
                    'parent': cls,
                    'roles': [role_rs]
                }
        return filter_roles

    if des_roles is None:
        des_roles = []
    if not roles:
        return {}

    filter_roles = dict()
    fields = DEFAULT_FIELDS + ",_links,absoluteName,range"
    migration_action = MigrationAction(action, cls_data)
    if roles and action not in [Actions.EXPOSE, Actions.HIDE, Actions.COPY, Actions.ADD_SERVERS, Actions.DELETE]:
        des_roles = des_roles[0]
    if action == Actions.COPY:
        if des_roles[0].get('type') == EntityV2.NETWORK_INTERFACE:
            for role in roles:
                if role.get('_inheritedFrom'):
                    g.user.logger.debug(
                        f"[MIGRATION][SKIP] {action.capitalize()} role: Skip copying to server for inherited role")
                    continue
                updated_role = migration_action.copy_role_to_server(role, interface_id=des_roles[0].get('id'))
                if updated_role:
                    filter_roles = update_f_roles(cls_data, updated_role, filter_roles)
        else:
            for des_role in des_roles:
                new_role = migration_action.copy_role_to_zone(roles[0], new_zone=des_role)
                filter_roles = update_f_roles(des_role, new_role, filter_roles)

    elif action == Actions.MOVE:
        for role in roles:
            if role.get('_inheritedFrom'):
                g.user.logger.debug(
                    f"[MIGRATION][SKIP] {action.capitalize()} role: Skip moving to server for inherited role")
                continue
            updated_role = migration_action.move_role_to_server(role=role, interface_id=des_roles.get('id'))
            if not updated_role:
                continue
            if not updated_role.get('is_exists') and not role.get('_inheritedFrom'):
                # delete origin role
                filter_roles = update_f_roles(cls_data, role, filter_roles, is_delete_role=True)
            if not updated_role.get('is_exists_duplicated_role'):
                filter_roles = update_f_roles(cls_data, updated_role, filter_roles)

    elif action == Actions.MOVE_PRIMARY:
        if_id = des_roles.get('id')
        for role in roles:
            role = rest_v2.get_deployment_role(role.get('id'))
            cls_type = EntityV2.get_collection(cls_data.get('type'))
            roles_of_cls = rest_v2.get_deployment_roles_by_collection(cls_type, cls_data.get('id')).get('data')
            dup_role = get_duplicate_role_by_server(current_role=role, interface_id=if_id, collection=cls_data)
            dup_role_type = dup_role.get('roleType')

            # The old Primary server becomes a Secondary, Hidden Primary becomes a Stealth Secondary.
            is_exists = False
            for current_role in roles_of_cls:
                c_role_type = current_role.get('roleType')
                if c_role_type in PRIMARY_GROUP:
                    update_f_roles(cls_data, convert_primary_role(current_role), filter_roles)
                if dup_role_type == c_role_type:
                    is_exists = True

            role_type = RoleType.HIDDEN_PRIMARY
            if dup_role:
                if dup_role_type in EXPOSE_ROLES:
                    dup_role['roleType'] = RoleType.PRIMARY
                    update_f_roles(cls_data, dup_role, filter_roles)
                    continue

                elif dup_role_type in (RoleType.STUB, RoleType.RECURSION, RoleType.FORWARDER):
                    g.user.logger.error(
                        f"[MIGRATION][SKIP] Move primary role: Existing recursive roles are conflict with the Primary "
                        f"role.")
                    return filter_roles
            if role_type:
                updated_role = dup_role if dup_role and not is_exists else {
                    "type": Entity.DeploymentRole,
                    "roleType": role_type,
                    "serverInterface": {"id": if_id}
                }
                update_f_roles(cls_data, updated_role, filter_roles)
    elif action == Actions.ADD_SERVERS:
        configuration_js = rest_v2.get_configuration_by_name(configuration_name).get('data')[0]
        for target in des_roles:
            new_role = {
                'roleType': target.get('role_type'),
                'configuration': configuration_js,
                'view': view_name or target.get('view'),
                'server_interface': target.get('name'),
                'zone_transfer_interface': target.get('zone_transfer_interface')

            }
            update_role = migration_action.add_servers(role=new_role, collection=cls_data)
            if update_role:
                filter_roles = update_f_roles(cls_data, update_role, filter_roles)

    if action in [Actions.EXPOSE, Actions.HIDE, Actions.DELETE]:
        for role in roles:
            if role.get('_inheritedFrom'):
                g.user.logger.debug(
                    f"[MIGRATION][SKIP] {action.capitalize()} role: Cannot {action} inherited role")
                continue
            up_href = common.get_links_href(role.get('_links'), 'up')
            rs = rest_v2.link_api(up_href, fields=fields)
            update_f_roles(rs, role, filter_roles, is_delete_role=action == Actions.DELETE)
    return filter_roles


class MigrationAction:
    def __init__(self, action, collection):
        self.action = action
        self.collection = collection

    def copy_role_to_zone(self, role, new_zone):
        try:
            rest_v2 = g.user.v2
            s_role = rest_v2.get_deployment_role(role.get('id'))
            if_id = s_role.get('serverInterface').get('id')
            d_roles = rest_v2.get_deployment_roles_by_collection(
                EntityV2.get_collection(new_zone.get('type')), new_zone.get('id')).get('data')
            for d_role in d_roles:
                if d_role.get('_inheritedFrom'):
                    g.user.logger.debug('[MIGRATE] Skipped, zone contains inherited roles')
                    d_roles = []
                    break
                d_role_type = d_role.get('roleType')
                if d_role_type in PRIMARY_GROUP and s_role.get('roleType') in PRIMARY_GROUP and d_role.get(
                        'serverInterface').get('id') != if_id:
                    g.user.logger.debug("[MIGRATE] Ignored, {} role already exists".format(d_role_type))
                    return

            dup_roles = [r for r in d_roles if r.get('serverInterface').get('id') == if_id]
            if dup_roles:
                role = self.merge_copy_role_to_zone(dup_roles[0], current_role=role)
        except Exception as e:
            g.user.logger.error(f"[MIGRATION][COPY_ROLE_TO_ZONE][SKIP] Failed to copied role to zone: {e}")
            raise e
        return role

    def copy_role_to_server(self, role, interface_id):
        try:
            rest_v2 = g.user.v2
            role = rest_v2.get_deployment_role(role.get('id'))
            if role.get('serverInterface').get('id') == interface_id:
                g.user.logger.debug("[SKIP] Ignored, cannot copy role {} to same server interface named {}.".format(
                    role.get('roleType'), role.get('serverInterface').get('name')))
                return
            if not validate_valid_zone_transfer_and_target_interface(role, interface_id):
                g.user.logger.debug("[SKIP] Ignored, cannot copy role {} to same server named {} with zone transfer "
                                    "interface.".format(role.get('roleType'), role.get('serverInterface').get('name')))
                return
            duplicate_role = get_duplicate_role_by_server(current_role=role, interface_id=interface_id,
                                                          collection=self.collection)
            if duplicate_role:
                role = self.merge_role(role=duplicate_role, current_role=convert_primary_role(role))
            else:
                server_interface_dict = {'id': interface_id}
                if role.get('roleType') == RoleType.PRIMARY:
                    role.update({'roleType': RoleType.SECONDARY})
                elif role.get('roleType') == RoleType.HIDDEN_PRIMARY:
                    role.update({'roleType': RoleType.STEALTH_SECONDARY})

                role['serverInterface'] = server_interface_dict
        except Exception as e:
            g.user.logger.error(f"[MIGRATION] Copied role to server action exception: {e}")
            raise e
        return role

    def merge_role(self, role, current_role):
        current_role_type = current_role.get('roleType')
        role_type = role.get('roleType')
        try:
            if role_type == RoleType.STEALTH_SECONDARY:
                if current_role_type in EXPOSE_ROLES + [RoleType.HIDDEN_PRIMARY]:
                    role['roleType'] = current_role_type
            elif role_type == RoleType.HIDDEN_PRIMARY:
                if current_role_type in EXPOSE_ROLES:
                    role['roleType'] = RoleType.PRIMARY
            elif role_type == RoleType.SECONDARY:
                if current_role_type in PRIMARY_GROUP:
                    role['roleType'] = RoleType.PRIMARY
            else:
                return
        except Exception as e:
            g.user.logger.error(f"[MIGRATION] Failed to merged role: {e}")
            raise e
        return role

    def merge_copy_role_to_zone(self, role, current_role):
        current_role_type = current_role.get('roleType')
        role_type = role.get('roleType')
        if role_type == current_role_type or role_type in [RoleType.FORWARDER, RoleType.STUB]:
            return
        if role_type == RoleType.STEALTH_SECONDARY:
            if current_role_type in (RoleType.PRIMARY, RoleType.SECONDARY, RoleType.HIDDEN_PRIMARY):
                role['roleType'] = current_role_type
        elif role_type == RoleType.HIDDEN_PRIMARY:
            if current_role_type in EXPOSE_ROLES:
                role['roleType'] = RoleType.PRIMARY
        elif role_type == RoleType.SECONDARY:
            if current_role_type in PRIMARY_GROUP:
                role['roleType'] = RoleType.PRIMARY
        return role

    def move_role_to_server(self, role, interface_id):
        try:
            rest_v2 = g.user.v2
            role = rest_v2.get_deployment_role(role.get('id'))
            is_exists = True if role.get('serverInterface').get('id') == interface_id else False
            if not validate_valid_zone_transfer_and_target_interface(role, interface_id):
                g.user.logger.debug("[SKIP] Ignored, cannot copy role {} to same server named {} with zone transfer "
                                    "interface.".format(role.get('roleType'), role.get('serverInterface').get('name')))
                return
            duplicate_role = get_duplicate_role_by_server(role, interface_id, self.collection)
            if duplicate_role:
                role = self.merge_move_role_to_server(role, duplicate_role)
            else:
                role['serverInterface'] = {'id': interface_id}
        except Exception as e:
            g.user.logger.error(f"[MIGRATION] Moved role to server action exception: {e}")
            raise e
        role['is_exists'] = True if is_exists else False
        return role

    def merge_move_role_to_server(self, current_role, duplicated_role):
        current_role_type = current_role.get('roleType')
        duplicated_role_type = duplicated_role.get('roleType')
        try:
            if duplicated_role_type == current_role_type:
                duplicated_role['is_exists_duplicated_role'] = True
                return duplicated_role

            if current_role_type == RoleType.HIDDEN_PRIMARY:
                current_role['roleType'] = RoleType.STEALTH_SECONDARY

            current_role_type = current_role.get('roleType')
            try:
                merged_role_type = get_merge_role_result(current_role_type, duplicated_role_type)
            except ActionConflictException as e:
                g.user.logger.warning(f"[MIGRATION][MOVE_ROLES][SKIP] Failed {e}")
            else:
                if duplicated_role_type != merged_role_type:
                    duplicated_role['roleType'] = merged_role_type
        except Exception as e:
            g.user.logger.error(f"[MIGRATION] Failed to merged role: {e}")
            raise e
        return duplicated_role

    def add_servers(self, role, collection):
        try:
            rest_v2 = g.user.v2
            role_type = role.get('roleType')
            if role_type.upper() not in (
                    RoleType.STEALTH_SECONDARY, RoleType.SECONDARY, RoleType.FORWARDER, RoleType.STUB):
                return
            zone_transfer_if = role.get('zone_transfer_interface')
            role = create_deployment_role_object(role.get('configuration'), role.get('view'), role.get('roleType'),
                                                 role.get('server_interface'), zone_transfer_if)
            duplicate_role = get_duplicate_role_in_zone(new_zone=collection,
                                                        interface_id=role.get('serverInterface').get('id'))
            updated_role = role
            if duplicate_role:
                updated_role = self.merge_copy_role_to_zone(role=duplicate_role, current_role=role)
                dup_zone_transfer = duplicate_role.get('zoneTransferServerInterface')
                if dup_zone_transfer:
                    dup_zone_transfer_name = rest_v2.get_entity_by_id(dup_zone_transfer.get('id')).get('name')
                    if dup_zone_transfer_name == zone_transfer_if:
                        g.user.logger.info(
                            f"[Migration][ADD_SERVERS] Conflicted Zone Transfer Server Interface: - Origin Interface: {dup_zone_transfer_name}, - New Interface: {zone_transfer_if}, will keep the origin Zone Transfer Interface.")

                if duplicate_role.get('roleType') in PRIMARY_GROUP:
                    updated_role['zone_transfer_interface'] = ''
        except Exception as e:
            g.user.logger.error(f"[MIGRATION] Added role to server action exception: {e}")
            raise e
        return updated_role


class MigrationXMLBuilder:
    def __init__(self, config_name, action, roles=None):
        if roles is None:
            roles = []

        self.tree = ET.ElementTree()
        self.root = ET.Element('data')
        self.tree._setroot(self.root)

        self.config_name = config_name
        self.view_name = ''
        self._handle_configuration()
        self.roles = roles
        self.action = action

        self.reverse_role = dict()
        self.forward_role = dict()
        self.deployment_options = []

    def update_filter_roles(self, filter_roles):
        def update(cls_id, cls_data, roles):
            if roles.get(cls_id):
                for role in cls_data.get('roles'):
                    roles[cls_id]['roles'].append(role)
            else:
                roles.update({cls_id: cls_data})
            return roles

        for key, val in filter_roles.items():
            if val.get('parent').get('type') in ZoneType.REVERSE_ZONE:
                update(key, val, self.reverse_role)
            else:
                update(key, val, self.forward_role)

    def write_to_file(self, migration_path, encode_type='utf-8'):
        config_file = get_config(MIGRATION_CONFIG)
        max_file_store = config_file.get("MIGRATION", "max_file_store", fallback="")
        max_file_store = MAX_FILE_STORE if not max_file_store else int(max_file_store)
        list_of_files = os.listdir(MIGRATION_PATH)
        full_path = ["{}/{}".format(MIGRATION_PATH, x) for x in list_of_files if 'dtd' not in x]
        if len(list_of_files) - 1 >= max_file_store:
            oldest_file = min(full_path, key=os.path.getctime)
            os.remove(oldest_file)

        with open(migration_path, 'wb') as f:
            xml_data = minidom.parseString(ET.tostring(self.root))
            dt = minidom.getDOMImplementation('').createDocumentType(
                DOCTYPE_QUALIFIED_NAME, DOCTYPE_PUBLIC_ID, DOCTYPE_SYSTEM_ID)
            xml_data.insertBefore(dt, xml_data.documentElement)
            f.write(xml_data.toprettyxml(indent="  ", encoding=encode_type))

    def get_ip_blocks(self, target):
        rest_v2 = g.user.v2
        blocks = [target.get("range")]
        block_href = common.get_links_href(target.get('_links'), 'up')
        while "block" in block_href:
            block_rs = rest_v2.link_api(block_href, "_links, range")
            blocks.append(block_rs.get('range'))
            block_href = common.get_links_href(block_rs.get('_links'), 'up')
        return blocks

    def execute(self):
        rest_v2 = g.user.v2
        parent_el = None
        filter_data = self.reverse_role | self.forward_role
        for data in filter_data.values():
            parent_role = data.get('parent')
            rs_type = parent_role.get('type')
            ip_type = 'v4' if 'v4' in rs_type else 'v6'
            target_deployment_ops = common.get_deployment_options_by_collection(parent_role).get('data')
            adding_deployment_ops = []
            for option in self.deployment_options:
                server = option.get('serverScope')
                if server:
                    if server.get('type') == Entity.Server:
                        if not server.get('name') in [role.get('serverInterface').get('server').get('name') for role in
                                                      data.get('roles')]:
                            continue
                    else:
                        server_collection = rest_v2.get_servers_in_server_group(server.get("id"))
                        if not any(
                                server in [ser.get('name') for ser in server_collection.get('data')] for server
                                in [role.get('serverInterface').get('server').get('name') for role in data.get('roles')]):
                            continue
                conflicted = False
                for op in target_deployment_ops:
                    if server == op.get('serverScope') and option.get('name') == op.get('name'):
                        conflicted = True
                        break
                if conflicted:
                    continue

                adding_deployment_ops.append(option)

            if rs_type in [EntityV2.IP4_BLOCK, EntityV2.IP6_BLOCK]:
                parent_blocks = self.get_ip_blocks(parent_role)
                parent_el = self._handle_configuration()
                for block in parent_blocks[::-1]:
                    parent_el = self._handle_block(parent_el, block, ip_type)
            elif rs_type in [EntityV2.IP4_NETWORK, EntityV2.IP6_NETWORK]:
                parent_blocks = self.get_ip_blocks(parent_role)
                parent_el = self._handle_network(parent_blocks, ip_type)
            elif rs_type == EntityV2.VIEW:
                parent_el = self._handle_view()
            elif rs_type == EntityV2.ZONE:
                ab_name = parent_role.get('absoluteName')
                if ab_name[-1] == '.':
                    g.user.debug("Ignore dot (.) at end of zone: {}".format(ab_name))
                    ab_name = ab_name[0:- 1]
                parent_el = self._handle_zone(ab_name)
            self._handle_role(parent_el, data.get('roles'))
            self._handle_option(parent_el, adding_deployment_ops)

    def _handle_option(self, parent, adding_deployment_ops):
        for option in adding_deployment_ops:
            option_el = ET.SubElement(parent, OpType.DNS_OPTION)
            option_el.set('name', option.get('name'))
            values = option.get('value')
            yes_no = {'yes': 'true', 'no': 'false'}
            server = option.get("serverScope")
            if server:
                if server.get('type') == "Server":
                    option_el.set('server', server.get("name"))
                elif server.get('type') == "ServerGroup":
                    option_el.set('server-group', server.get("name"))
            if isinstance(values, list):
                for value in values:
                    if isinstance(value, list):
                        option_value = ''
                        for attrib in value:
                            option_value = option_value + str(attrib) + ','
                        value_el = ET.SubElement(option_el, OpType.OPTION_VALUE)
                        value_el.set("value", option_value)
                    else:
                        value_el = ET.SubElement(option_el, OpType.OPTION_VALUE)
                        value_el.set("value", yes_no.get(str(value), str(value)))
                continue
            value = option.get('value')
            option_el.set('value', yes_no.get(str(value), str(value)))

    def _handle_role(self, parent, roles, on_exist=OnExist.RECREATE_TREE):
        rest_v2 = g.user.v2
        for role in roles:
            if_id = role.get('serverInterface').get('id')
            if_rs = rest_v2.get_entity_by_id(if_id)
            up_href = common.get_links_href(if_rs.get('_links'), 'up')
            server = rest_v2.link_api(up_href)
            server_name = server.get('name')

            role_el = ET.SubElement(parent, OpType.DNS_ROLE)
            role_el.set('server', server_name)
            role_el.set('server-hostname', if_rs.get('name'))
            if parent.tag not in [OpType.VIEW, OpType.ZONE]:
                role_el.set('view', self.view_name)
            # TODO: BAM 9.5 doesn't support published interface, currently, always migrate Network interface
            # server_if_cls = self.rest_v2.link_api(common.get_links_href(if_rs.get('_links'), 'self'),
            #                                       "id,name,type,managementAddress,primaryAddress")
            # role_el.set('server-ip', server_if_cls.get('managementAddress') or server_if_cls.get('primaryAddress'))
            role_type = role.get('roleType')
            if self.action == Actions.EXPOSE:
                role_type = RoleType.PRIMARY if role_type == RoleType.HIDDEN_PRIMARY else RoleType.SECONDARY
            elif self.action == Actions.HIDE:
                role_type = RoleType.STEALTH_SECONDARY if role_type == RoleType.SECONDARY else RoleType.HIDDEN_PRIMARY

            role_el.set('type', DNSDeploymentRoles.get_migration_type(role_type))
            zone_transfer = role.get('zoneTransferServerInterface', {}) or {}
            role_el.set('zone-transfer-interface', zone_transfer.get('name') or "")
            role_el.set('on-exist', role.get('on-exist') or on_exist)

    def _handle_configuration(self, on_exist=''):
        configurations = self.root.findall("./{}[@name='{}']".format(OpType.CONFIG, self.config_name))
        if len(configurations) > 0:
            return configurations[0]
        # Create configuration
        configuration = ET.SubElement(self.root, OpType.CONFIG)
        configuration.set('name', self.config_name)
        if on_exist:
            configuration.set('on-exist', on_exist)
        return configuration

    def _handle_view(self, on_exist=''):
        configuration = self._handle_configuration()
        views = configuration.findall("./{}[@name='{}']".format(OpType.VIEW, self.view_name))
        if len(views) > 0:
            return views[0]
        # create view
        view = ET.SubElement(configuration, OpType.VIEW)
        view.set('name', self.view_name)
        if on_exist:
            view.set('on-exist', on_exist)
        return view

    def _handle_zone(self, full_zone_name, on_exist=""):
        view = self._handle_view()
        if full_zone_name[-1] == '.':
            g.user.logger.debug("Ignore dot (.) at end of zone: {}".format(full_zone_name))
            full_zone_name = full_zone_name[0:- 1]
        list_zone = full_zone_name.split('.')
        list_zone.reverse()
        parent = view
        # Example after reverse:
        # list_zone = [corp1, test1, sub1]
        for index in range(len(list_zone)):
            p_zone = list_zone[index]
            zones = parent.findall("./{}[@name='{}']".format(OpType.ZONE, p_zone))
            if len(zones) > 0:
                parent = zones[0]
            else:
                zone = ET.SubElement(parent, OpType.ZONE)
                zone.set('name', p_zone)
                if index == len(list_zone) - 1 and on_exist:
                    zone.set('on-exist', on_exist)
                parent = zone
        return parent

    def _handle_block(self, parent, b_range, ip_type='v4', on_exist=""):
        op_type = OpType.IP4_BLOCK if ip_type == 'v4' else OpType.IP6_BLOCK
        block = parent.findall("./{}[@range='{}']".format(op_type, b_range))
        if len(block) > 0:
            return block[0]
        block = ET.SubElement(parent, op_type)
        if ip_type == 'v4':
            block.set('range', b_range)
        else:
            block.set('block', b_range)
        if on_exist:
            block.set('on-exist', on_exist)
        return block

    def _handle_network(self, parent_blocks, ip_type='v4', on_exist=""):
        network_range = parent_blocks[0]
        parent_el = self._handle_configuration()
        for block in parent_blocks[:0:-1]:
            parent_el = self._handle_block(parent_el, block, ip_type)
        op_type = OpType.IP4_NETWORK if ip_type == 'v4' else OpType.IP6_NETWORK
        network = parent_el.findall("./{}[@range='{}']".format(op_type, network_range))
        if len(network) > 0:
            return network[0]
        # Create network
        network = ET.SubElement(parent_el, op_type)
        if ip_type == 'v4':
            network.set('range', network_range)
        else:
            network.set('network', network_range)
        if on_exist:
            network.set('on-exist', on_exist)
        return network
