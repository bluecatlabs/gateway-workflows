# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
import datetime
import traceback

from flask import jsonify, g, make_response, send_file
from flask_restx import Resource

from bluecat import util
from bluecat.gateway.decorators import require_permission

from .library.parsers.deployment_role_parsers import (
    deployment_role_parser,
    deployment_role_action_parser,
    deployment_role_migration_parser, dns_deployment_role_parser
)

from .. import bp_rm
from ..common.common import (
    get_ipv4_range_from_reverse_zone,
    get_ipv6_range_from_reverse_zone)
from ..common.migrations import MigrationXMLBuilder
from ..common.validations import RoleValidation
from ..rest_v2 import common
from ..rest_v2.common import group_by_role_of_server
from ..rest_v2.constants import (
    GroupOption,
    RoleGroup,
    Actions,
    Collections,
    ZoneTypeCls,
    HIDE_ROLES,
    EXPOSE_ROLES,
    EntityV2,
    enable_copy_dns_option
)
from ..common import actions, migrations
from ..common.exception import UserException, InvalidParam
from ..common.constants import MIGRATION_PATH, Status
from ..rest_v2.decorators import rest_v2_handler

deployment_role_ns = bp_rm.namespace(
    'Deployment Role Resources',
    path='/configuration/<configuration_name>/deployment_roles',
    description='Deployment Roles operations',
)

dns_deployment_role_ns = bp_rm.namespace(
    'DNS Deployment Role Resources',
    path='/configuration/<configuration_name>/view/<view_name>/dns_deployment_roles',
    description='DNS Deployment Roles operations',
)


@require_permission('rest_page')
@deployment_role_ns.route('')
class Roles(Resource):
    @rest_v2_handler
    @util.no_cache
    @deployment_role_ns.expect(deployment_role_parser, validate=True)
    def get(self, configuration_name):
        """ Get all known Deployment Role(s). """
        try:
            if not g.user:
                return make_response("Authentication is required.", 401)
            total_by_server = 0
            bam_api = g.user.v2
            data = deployment_role_parser.parse_args()
            group = data.get('group_by')
            filter_role_group = data.get('role_groups')
            filter_role = data.get('custom_role_group')
            if filter_role and filter_role_group != RoleGroup.ALL:
                raise UserException("Get Role function can be filter by Role Group or Custom Role Group only.")
            filter_server_interface = data.get('server_interface_names')
            filter_server = data.get('server_names')
            filter_view = data.get('view_names')
            filter_zone = data.get('zone_names')
            blocks = data.get('blocks')
            networks = data.get('networks')
            start = data.get('offset', 0)
            count = data.get('limit', 100)
            configuration = bam_api.get_configuration_by_name(configuration_name)
            configuration_id = configuration.get('data')[0].get('id')
            filter = "ancestor.id: {}".format(str(configuration_id))
            if filter_role:
                filter += " and {}".format(common.filter_role_type(filter_role))
            elif filter_role_group != RoleGroup.ALL:
                filter += " and {}".format(common.filter_by_role_groups(filter_role_group))
            if filter_view:
                view_name_filter, view_id_filter = common.filter_by_view(configuration_id, filter_view)
                filter = "{} and {} or {} and {}".format(filter, view_name_filter, filter, view_id_filter)
            list_roles = common.list_all_roles(bam_api.get_deployment_roles(filter),
                                               configuration_id=configuration_id)
            list_roles = common.filter_roles(list_roles, zone_names=filter_zone, blocks=blocks, networks=networks,
                                             interfaces=filter_server_interface, servers=filter_server)
            if group == GroupOption.BY_ROLE_SERVER:
                list_roles, total_by_server = group_by_role_of_server(list_roles, start, count)
            elif not group == GroupOption.ALL_ROLES:
                list_roles = common.group_roles_by_option(list_roles, group)

            total = total_by_server if group == GroupOption.BY_ROLE_SERVER else len(list_roles)
            count = total - start if int(count) > total - start else count
            end = int(start) + int(count)
            result = {
                'total': total,
                'data': list_roles[int(start): end] if group != GroupOption.BY_ROLE_SERVER else list_roles,
                'start': int(start),
                'count': int(count)
            }
            return make_response(jsonify(result))
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)

    @rest_v2_handler
    @util.no_cache
    @deployment_role_ns.expect(deployment_role_action_parser, validate=True)
    def post(self, configuration_name):
        """ Deployment Roles actions. """
        if not g.user:
            return make_response("Authentication is required.", 401)
        try:
            data = deployment_role_action_parser.parse_args()
            action = data.get('action')
            validate = data.get('validate')
            option_filter = data.get("options")
            # TODO: Define a model for roles
            roles = data.get('roles')[0] if data.get('roles') else []
            target_roles = data.get('target_roles')[0] if data.get('target_roles') else []
            if not roles:
                raise InvalidParam('Missing Roles')
            if not target_roles and action not in [Actions.EXPOSE, Actions.HIDE, Actions.DELETE]:
                raise InvalidParam('Missing target roles data for action named {}'.format(action))

            rest_v2 = g.user.v2
            configuration_js = rest_v2.get_configuration_by_name(configuration_name).get('data')[0]
            des_cls = common.get_target_collection_data(configuration_js, action, target_roles) \
                if action != [Actions.EXPOSE, Actions.HIDE, Actions.DELETE] else []
            if validate:
                validator = RoleValidation(action=action)
                validation_result = validator.validate(roles=roles, target=des_cls, configuration=configuration_js)
                return make_response(jsonify(validation_result))
            result, status, fetched_roles = [], [], []
            role_action = actions.RoleAction(action, validate)
            for role in roles:
                role_type = role.get('role_type', '').upper()
                server_interface = role.get('server_interface')
                cls_data = role_status = dict()
                view = role.get('view')
                try:
                    cls_data = common.get_collection_data(configuration_js, role)
                    role_action.set_role_collection(cls_data)
                    dep_roles = common.get_deployment_roles_by_collection(cls_data, server_interface, view)
                    if action == Actions.COPY:
                        dep_roles = [dep_role for dep_role in dep_roles if dep_role.get('roleType') == role_type]
                        if dep_roles:
                            if des_cls and des_cls[0].get('type') in (
                                    EntityV2.ZONE, EntityV2.IP4_BLOCK, EntityV2.IP4_NETWORK, EntityV2.IP6_BLOCK,
                                    EntityV2.IP6_NETWORK):
                                # TODO: support copy role(s) to zone (currently, only get first value)
                                dep_role = dep_roles[0]
                                dep_role['collection'] = cls_data
                                fetched_roles.append(dep_role)
                                if role == roles[-1]:
                                    for fetched_role in fetched_roles:
                                        collection = fetched_role.get('collection')
                                        role_action.set_role_collection(collection)
                                        for target_zone in des_cls:
                                            status = role_action.validate_and_copy_role_to_zone(role=fetched_role,
                                                                                                new_zone=target_zone,
                                                                                                option_filter=option_filter)
                                            result.append(get_formatted_action_result(status, collection))
                                continue
                            else:
                                status = role_action.validate_and_copy_role_to_server(role=dep_roles[0],
                                                                                      new_server_interface_id=des_cls[
                                                                                          0].get('id'))
                        else:
                            status = {
                                "roleType": role_type,
                                "message": "Role not found",
                                'status': Status.FAILED,
                            }
                    elif action == Actions.MOVE:
                        dep_roles = [dep_role for dep_role in dep_roles if dep_role.get('roleType') == role_type]
                        if not dep_roles:
                            status = {
                                "roleType": role_type,
                                "message": "Role not found",
                                'status': Status.FAILED,
                            }
                            result.append(get_formatted_action_result(status, cls_data))
                        for dep_role in dep_roles:
                            dep_role['collection'] = cls_data
                        fetched_roles.extend(dep_roles)
                        if role == roles[-1]:
                            for fetched_role in fetched_roles:
                                collection = fetched_role.get('collection')
                                role_action.set_role_collection(collection)
                                status = role_action.validate_and_move_role_to_server(role=fetched_role,
                                                                                      new_server_interface_id=des_cls[
                                                                                          0].get('id'))
                                result.append(get_formatted_action_result(status, collection))
                        continue
                    elif action == Actions.MOVE_PRIMARY:
                        dep_roles = [dep_role for dep_role in dep_roles if dep_role.get('roleType') == role_type]
                        if dep_roles:
                            status = role_action.validate_and_move_primary_role(role=dep_roles[0],
                                                                                new_server_interface_id=des_cls[0].get(
                                                                                    'id'))
                    elif action == Actions.ADD_SERVERS:
                        for target in des_cls:
                            if not target.get('role_type'):
                                raise InvalidParam("Missing role_type for add server roles action")
                            new_role = {
                                'roleType': target.get('role_type'),
                                'configuration': configuration_js,
                                'view': role.get('view', target.get('view')),
                                'server_interface': target.get('name'),
                                'zone_transfer_interface': target.get('zone_transfer_interface'),

                            }
                            status = role_action.add_servers(role=new_role, collection=cls_data)
                            result.append(get_formatted_action_result(status, cls_data))
                        continue
                    elif action in [Actions.EXPOSE, Actions.HIDE, Actions.DELETE]:
                        if action == Actions.EXPOSE and role_type and role_type not in HIDE_ROLES:
                            raise InvalidParam('Cannot make visible with role type {}.'.format(role_type))
                        if action == Actions.HIDE and role_type and role_type not in EXPOSE_ROLES:
                            raise InvalidParam('Cannot make invisible for role type {}.'.format(role_type))
                        action_roles_group = EXPOSE_ROLES if action == Actions.EXPOSE \
                            else HIDE_ROLES if action == Actions.HIDE else []
                        filter_role = action_roles_group if not role_type else [role_type]
                        dep_roles = [dep_role for dep_role in dep_roles if dep_role.get('roleType') in filter_role]
                        if not dep_roles:
                            status = {
                                "roleType": role_type,
                                "message": "Role not found",
                                'status': Status.FAILED,
                            }
                            result.append(get_formatted_action_result(status, cls_data))

                        for dep_role in dep_roles:
                            dep_role['collection'] = cls_data
                        fetched_roles.extend(dep_roles)
                        if role == roles[-1]:
                            if action == Actions.EXPOSE:
                                statuses = role_action.expose_roles(fetched_roles)
                            elif action == Actions.HIDE:
                                statuses = role_action.hide_roles(fetched_roles)
                            else:
                                statuses = role_action.delete_roles(fetched_roles)
                            for index, status in enumerate(statuses):
                                collection = fetched_roles[index].get('collection')
                                result.append(get_formatted_action_result(status, collection))
                        continue

                except Exception as ex:
                    g.user.logger.warning(
                        'Failed to get role data: {}, skip for collection {}'.format(str(ex), cls_data))
                    status = {
                        "roleType": role_type,
                        'message': str(ex),
                        'status': Status.FAILED
                    }
                if not status.get('targetRoleType'):
                    status['targetRoleType'] = status.get('roleType')
                role_status['status'] = status
                if cls_data.get('name'):
                    role_status['name'] = cls_data.get('name')
                if cls_data.get('type'):
                    role_status['type'] = cls_data.get('type')
                if role.get('collection') == Collections.ZONES and cls_data.get('absoluteName'):
                    role_status['absoluteName'] = cls_data.get('absoluteName')
                elif role.get('collection') in ZoneTypeCls.REVERSE_ZONE and cls_data.get('range'):
                    role_status['range'] = cls_data.get('range')
                result.append(role_status)
            return make_response(jsonify(result))
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@require_permission('rest_page')
@dns_deployment_role_ns.route('')
class DNSRoles(Resource):
    @rest_v2_handler
    @util.no_cache
    @dns_deployment_role_ns.expect(dns_deployment_role_parser, validate=True)
    def get(self, configuration_name, view_name):
        """ Get all known Deployment Role(s). """
        try:
            if not g.user:
                return make_response("Authentication is required.", 401)
            total_by_server = 0
            bam_api = g.user.v2
            data = dns_deployment_role_parser.parse_args()
            group = data.get('group_by')
            is_contain_inherited = data.get('contain_inherited')
            filter_role_group = data.get('role_groups')
            filter_role = data.get('custom_role_group')
            if filter_role and filter_role_group != RoleGroup.ALL:
                raise UserException("Get Role function can be filter by Role Group or Custom Role Group only.")
            filter_server_interface = data.get('server_interface_names')
            filter_server = data.get('server_names')
            filter_zones = data.get('zone_names')
            filter_blocks = data.get('blocks')
            filter_networks = data.get('networks')
            start = data.get('offset', 0)
            count = data.get('limit', 100)
            configuration = bam_api.get_configuration_by_name(configuration_name)
            configuration_id = configuration.get('data')[0].get('id')
            view = bam_api.get_view_by_name(view_name=view_name, filter='ancestor.id:{}'.format(configuration_id))
            view_id = view.get('data')[0].get('id')
            filter_statements = []
            filter_view = "view.id: {}".format(str(view_id))
            filter = ''
            if filter_role:
                if filter:
                    filter += 'and '
                filter += " {}".format(common.filter_role_type(filter_role))
            elif filter_role_group != RoleGroup.ALL:
                if filter:
                    filter += 'and '
                filter += " {}".format(common.filter_by_role_groups(filter_role_group))
            filter_zones_dict = {}
            if filter_zones:
                zone_names = []
                for zone_name in filter_zones.split(','):
                    zone_name = zone_name.strip()
                    zone_names.append('"{}"'.format(zone_name))
                zone_list = bam_api.get_zones(filters='ancestor.id: {} and absoluteName: in({})'
                                              .format(view_id, ','.join(zone_names))).get('data')
                filter_zones_dict.update(
                    {str(zone.get('id')): zone for zone in zone_list}
                )
                if filter_zones_dict:
                    filter_zone_statement = filter + ' and ' if filter else ''
                    filter_zone_statement += ' ancestor.id: in({})'.format(','.join(filter_zones_dict.keys()))
                    filter_statements.append(filter_zone_statement)

            filter_block_dict = {}
            if filter_blocks:
                block_list = []
                for reverse_block_range in filter_blocks.split(','):
                    reverse_block_range = reverse_block_range.strip()
                    if 'ip6' not in reverse_block_range:
                        ipv4_range = get_ipv4_range_from_reverse_zone(reverse_block_range)
                        filter_str = 'ancestor.id:{} and range:eq("{}")'.format(configuration_id, ipv4_range)
                    else:
                        ipv6_range = get_ipv6_range_from_reverse_zone(reverse_block_range)
                        filter_str = 'ancestor.id:{} and range:eq("{}")'.format(configuration_id, ipv6_range)
                    block = bam_api.get_blocks(filters=filter_str).get('data')
                    block_list.extend(block)
                filter_block_dict.update(
                    {str(block.get('id')): block for block in block_list}
                )
                if filter_block_dict:
                    filter_block_statement = filter + ' and ' if filter else ''
                    filter_block_statement = filter_view + ' and ' + filter_block_statement + ' ancestor.id: in({})'\
                        .format(','.join(filter_block_dict.keys()))
                    filter_statements.append(filter_block_statement)

            # Filter networks
            filter_network_dict = {}
            if filter_networks:
                network_list = []
                for reverse_network_range in filter_networks.split(','):
                    reverse_network_range = reverse_network_range.strip()
                    if 'ip6' not in reverse_network_range:
                        ipv4_range = get_ipv4_range_from_reverse_zone(reverse_network_range)
                        filter_str = 'ancestor.id:{} and range:eq("{}")'.format(configuration_id, ipv4_range)
                    else:
                        ipv6_range = get_ipv6_range_from_reverse_zone(reverse_network_range)
                        filter_str = 'ancestor.id:{} and range:eq("{}")'.format(configuration_id, ipv6_range)
                    network = bam_api.get_networks(filters=filter_str).get('data')
                    network_list.extend(network)
                filter_network_dict.update(
                    {str(network.get('id')): network for network in network_list}
                )
                if filter_network_dict:
                    filter_network_statement = filter + ' and ' if filter else ''

                    filter_network_statement = filter_view + ' and ' + filter_network_statement + ' ancestor.id: in({})' \
                        .format(','.join(filter_network_dict.keys()))
                    filter_statements.append(filter_network_statement)

            if not filter_zones and not filter_networks and not filter_blocks:
                network_list = bam_api.get_networks(filters='ancestor.id:{}'.format(configuration_id)).get('data')
                filter_network_dict.update(
                    {str(network.get('id')): network for network in network_list}
                )
                block_list = bam_api.get_blocks(filters='ancestor.id:{}'.format(configuration_id)).get('data')
                filter_block_dict.update(
                    {str(block.get('id')): block for block in block_list}
                )
                zone_list = bam_api.get_zones(filters='ancestor.id:{}'.format(view_id)).get('data')
                filter_zones_dict.update(
                    {str(zone.get('id')): zone for zone in zone_list}
                )
            elif not filter_statements:
                result = {
                    'total': 0,
                    'data': [],
                    'start': 0,
                    'count': 0
                }
                return make_response(jsonify(result))

            single_filter = filter + ' and ' if filter else ''
            single_filter = '{} {} or {} ancestor.id: {}'.format(single_filter, filter_view, single_filter, view_id)
            list_roles = bam_api.get_deployment_roles(' or '.join(filter_statements) if filter_statements
                                                      else single_filter).get('data')
            list_roles = common.get_filtered_roles(list_roles, zone_dict=filter_zones_dict,
                                                   block_dict=filter_block_dict, network_dict=filter_network_dict,
                                                   view_id=view_id,
                                                   interfaces=filter_server_interface, servers=filter_server,
                                                   api=bam_api, is_inherited=is_contain_inherited, filters=filter)

            if group == GroupOption.BY_ROLE_SERVER:
                list_roles, total_by_server = group_by_role_of_server(list_roles, start, count)
            elif not group == GroupOption.ALL_ROLES:
                list_roles = common.group_roles_by_option(list_roles, group)

            total = total_by_server if group == GroupOption.BY_ROLE_SERVER else len(list_roles)
            count = total - start if int(count) > total - start else count
            end = int(start) + int(count)
            result = {
                'total': total,
                'data': list_roles[int(start): end] if group != GroupOption.BY_ROLE_SERVER else list_roles,
                'start': int(start),
                'count': int(count)
            }
            return make_response(jsonify(result))
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@require_permission('rest_page')
@deployment_role_ns.route('/migration')
class MigrationRoles(Resource):
    @rest_v2_handler
    @util.no_cache
    @deployment_role_ns.expect(deployment_role_migration_parser, validate=True)
    def post(self, configuration_name):
        """ Migrate and deploy deployment Roles. """
        if not g.user:
            return make_response("Authentication is required.", 401)
        try:
            data = deployment_role_migration_parser.parse_args()
            action = data.get('action')
            # TODO: need to define a model for roles
            roles = data.get('roles')[0] if data.get('roles') else []
            target_roles = data.get('target_roles')[0] if data.get('target_roles') else []
            if not roles:
                raise InvalidParam('Missing Roles')
            if not target_roles and action not in [Actions.EXPOSE, Actions.HIDE, Actions.DELETE]:
                raise InvalidParam('Missing target roles data for action named {}.'.format(action))

            rest_v2 = g.user.v2
            configuration_js = rest_v2.get_configuration_by_name(configuration_name).get('data')[0]
            des_cls = common.get_target_collection_data(configuration_js, action, target_roles)\
                if action != [Actions.EXPOSE, Actions.HIDE] else []

            copy_to_zone = action == Actions.COPY and target_roles[0].get(
                'collection') in [Collections.ZONES, Collections.BLOCKS, Collections.NETWORKS] and enable_copy_dns_option
            migration_builder = MigrationXMLBuilder(configuration_name, action)
            for role in roles:
                role_type = role.get('role_type', '').upper()
                server_interface = role.get('server_interface')
                cls_data = dict()
                view = role.get('view')
                filter_role = [role_type] if role_type else []
                try:
                    cls_data = common.get_collection_data(configuration_js, role)
                    dep_roles = common.get_deployment_roles_by_collection(cls_data, server_interface, view)
                    if copy_to_zone:
                        dep_ops = common.get_deployment_options_by_collection(cls_data)
                        cls_option = []
                        for option in dep_ops.get('data'):
                            if option.get('serverScope') in [seen.get('serverScope') for seen in
                                                             migration_builder.deployment_options if
                                                             seen.get('name') == option.get('name')]:
                                continue
                            cls_option.append(option)

                        option_filter = data.get("options")
                        new_cls_option = []
                        for option in cls_option:
                            for i in range(0, len(option_filter)):
                                if option.get("name") == option_filter[i].get("name"):
                                    opt_value = option_filter[i].get("value")
                                    if opt_value and option.get("value") != opt_value:
                                        continue
                                    new_cls_option.append(option)
                                    break
                        migration_builder.deployment_options.extend(new_cls_option)
                    if not migration_builder.view_name:
                        migration_builder.view_name = dep_roles[0].get('view').get('name')
                    if action == Actions.EXPOSE:
                        if role_type and role_type not in HIDE_ROLES:
                            g.user.logger.debug('[SKIP] Cannot make visible with role type {}.'.format(role_type))
                            continue
                        filter_role = HIDE_ROLES if not role_type else [role_type]
                    elif action == Actions.HIDE:
                        if role_type and role_type not in EXPOSE_ROLES:
                            g.user.logger.debug('[SKIP] Cannot hide for role type {}.'.format(role_type))
                            continue
                        filter_role = EXPOSE_ROLES if not role_type else [role_type]
                    if filter_role:
                        dep_roles = [dep_role for dep_role in dep_roles if dep_role.get('roleType') in filter_role]
                    role_data = migrations.group_role_by_parent_id(cls_data, action, dep_roles, configuration_name,
                                                                   role.get('view'), des_cls)
                    migration_builder.update_filter_roles(role_data)
                except Exception as ex:
                    if 'Not found deployment roles' in str(ex):
                        continue
                    err_mess = 'Failed to get role data: {}'.format(str(ex))
                    g.user.logger.warning(
                        err_mess + ', skip collection: {}'.format(cls_data) if cls_data else err_mess)
                    raise ex

            migration_builder.execute()
            migration_path = '{}/migration-{}.xml'.format(MIGRATION_PATH, datetime.datetime.now().isoformat())
            migration_builder.write_to_file(migration_path)
            return send_file(migration_path, mimetype='application/xml', as_attachment=True)
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


def get_formatted_action_result(status, cls_data):
    if not status.get('targetRoleType'):
        status['targetRoleType'] = status.get('roleType')
    role_status = {key: cls_data[key] for key in ['name', 'absoluteName', 'range', 'type'] if cls_data.get(key)}
    role_status['status'] = status
    return role_status
