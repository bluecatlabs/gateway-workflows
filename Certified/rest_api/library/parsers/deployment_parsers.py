# Copyright 2020 BlueCat Networks. All rights reserved.

from flask_restplus import reqparse

deployment_option_post_parser = reqparse.RequestParser()
deployment_option_post_parser.add_argument('name', location="json", help='Name of the Deployment Option')
deployment_option_post_parser.add_argument('value', location="json",
                                           help='Value to assign to the Deployment Option')
deployment_option_post_parser.add_argument('properties', location="json",
                                           help='Properties of the Deployment Option')

deployment_role_post_parser = reqparse.RequestParser()
deployment_role_post_parser.add_argument('server_fqdn', location="json",
                                         help='FQDN of server interface (Network or Published) to be assigned the role')
deployment_role_post_parser.add_argument('role_type', location="json",
                                         help='Type of role to assign (dns or dhcp)')
deployment_role_post_parser.add_argument('properties', location="json", help='Properties for the role'
                                         )
deployment_role_post_parser.add_argument('secondary_fqdn', location="json",
                                         help='FQDN of secondary interface, for DHCP Failover or Zone Transfer Interface')
deployment_role_post_parser.add_argument('role', location="json", help='Role to assign (master, slave, etc.)')
