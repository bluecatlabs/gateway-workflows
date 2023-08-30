# Copyright 2023 BlueCat Networks. All rights reserved.
from flask_restx import reqparse, inputs
from ....rest_v2.constants import Actions, RoleGroup

deployment_role_parser = reqparse.RequestParser()
deployment_role_parser.add_argument('group_by', required=True, choices=
("allRoles", "parentEntity", "serverInterface", "roleType", "roleServer"), location="args")
deployment_role_parser.add_argument('role_groups', required=True, choices=
(RoleGroup.ALL, RoleGroup.AUTHORITATIVE, RoleGroup.PRIMARY, RoleGroup.EXPOSED, RoleGroup.RECURSION,
 RoleGroup.FORWARDING), location="args")
deployment_role_parser.add_argument('custom_role_group', help='Type of the Deployment Role', default='',
                                    location="args", type=str)
deployment_role_parser.add_argument('server_interface_names', location="args",
                                    help='Server interface names of the Deployment Roles', default='')
deployment_role_parser.add_argument('server_names', location="args",
                                    help='Server names of the Deployment Roles', default='')
deployment_role_parser.add_argument('view_names', location="args", type=str,
                                    help='View names of the Deployment Roles', default='')
deployment_role_parser.add_argument('zone_names', location="args", type=str,
                                    help='Zone names of the Deployment Roles', default='')
deployment_role_parser.add_argument('blocks', location="args", type=str,
                                    help='Reverse Zone names of Blocks', default='')
deployment_role_parser.add_argument('networks', location="args", type=str,
                                    help='Reverse Zone names of Networks', default='')
deployment_role_parser.add_argument('limit', location="args",
                                    help='The maximum number of resources returned in the response.', type=int,
                                    default=100)
deployment_role_parser.add_argument('offset', location="args",
                                    help='The offset of the first resource returned in the response.', type=int,
                                    default=0)

dns_deployment_role_parser = reqparse.RequestParser()
dns_deployment_role_parser.add_argument('group_by', required=True, choices=
("allRoles", "parentEntity", "serverInterface", "roleType", "roleServer"), location="args")
dns_deployment_role_parser.add_argument('role_groups', required=True, choices=
(RoleGroup.ALL, RoleGroup.AUTHORITATIVE, RoleGroup.PRIMARY, RoleGroup.EXPOSED, RoleGroup.RECURSION,
 RoleGroup.FORWARDING), location="args")
dns_deployment_role_parser.add_argument('contain_inherited', required=True, type=inputs.boolean, default=False,
                                        location="args")
dns_deployment_role_parser.add_argument('custom_role_group', help='Type of the Deployment Role', default='',
                                        location="args", type=str)
dns_deployment_role_parser.add_argument('server_interface_names', location="args",
                                        help='Server interface names of the Deployment Roles', default='')
dns_deployment_role_parser.add_argument('server_names', location="args",
                                        help='Server names of the Deployment Roles', default='')
dns_deployment_role_parser.add_argument('zone_names', location="args", type=str,
                                        help='Zone names of the Deployment Roles', default='')
dns_deployment_role_parser.add_argument('blocks', location="args", type=str,
                                        help='Reverse Zone names of Blocks', default='')
dns_deployment_role_parser.add_argument('networks', location="args", type=str,
                                        help='Reverse Zone names of Networks', default='')
dns_deployment_role_parser.add_argument('limit', location="args",
                                        help='The maximum number of resources returned in the response.', type=int,
                                        default=100)
dns_deployment_role_parser.add_argument('offset', location="args",
                                        help='The offset of the first resource returned in the response.', type=int,
                                        default=0)

deployment_role_action_parser = reqparse.RequestParser()
deployment_role_action_parser.add_argument('action', required=True, choices=tuple(Actions.all()), location="args")

deployment_role_action_parser.add_argument('validate', required=True, type=inputs.boolean, default=False,
                                           location="args")

deployment_role_action_parser.add_argument('roles', location="json", default=[], required=True, type=list,
                                           action='append', help='List role data')
deployment_role_action_parser.add_argument('target_roles', location="json", default=[], type=list,
                                           action='append', help='List target role data')
deployment_role_action_parser.add_argument('options', location="json", default=[], type=list,
                                            help='List role options data')

deployment_role_migration_parser = reqparse.RequestParser()
deployment_role_migration_parser.add_argument('action', required=True, choices=tuple(Actions.all()), location="args")

deployment_role_migration_parser.add_argument('roles', location="json", default=[], required=True, type=list,
                                              action='append', help='List role data')
deployment_role_migration_parser.add_argument('target_roles', location="json", default=[], type=list,
                                              action='append', help='List target role data')
deployment_role_migration_parser.add_argument('options', location="json", default=[], type=list,
                                              help='List role options data')
