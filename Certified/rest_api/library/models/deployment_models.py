# Copyright 2020 BlueCat Networks. All rights reserved.

from flask_restplus import fields

from main_app import api

deployment_option_post_model = api.model(
    'deployment_options',
    {
        'name': fields.String(required=True, description='Name of the Deployment Option'),
        'value': fields.String(required=True,
                               description='Comma separated values to assign to the Deployment Option'),
        'properties': fields.String(required=False, description='Additional properties for the Deployment Option'),
    },
)

deployment_role_post_model = api.model(
    'deployment_roles',
    {
        'server_fqdn': fields.String(required=True,
                                          description='Name of the server interface the role will be assigned to'),
        'role_type': fields.String(required=True, description='Type of Deployment Role to assign (dns or dhcp)'),
        'role': fields.String(required=True, description='Role to assign (master, slave, etc.'),
        'properties': fields.String(required=False, description='Properties of the Deployment Role'),
        'secondary_fqdn': fields.String(required=False,
                                          description='Name of secondary server interface, if using DHCP Failover'),
    },
)
