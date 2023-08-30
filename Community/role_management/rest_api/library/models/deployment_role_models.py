# Copyright 2023 BlueCat Networks. All rights reserved.

from flask_restx import fields

from .... import bp_rm

filter_deployment_role_model = bp_rm.model(
    'deployment_role_filter',
    {
        'role_type': fields.String(required=False, description='Type of the Deployment Role'),
        'server_interface_name': fields.Integer(required=False,
                                                description='Server interface name of the Deployment Role'),
        'server_name': fields.Integer(required=False,
                                      description='Server name of the Deployment Role'),
        'view_name': fields.Integer(required=False, description='View name of the Deployment Role'),
        'zone_name': fields.Integer(required=False, description='Zone or Reverse Zone name of the Deployment Role'),
        'limit': fields.Integer(required=False,
                                description='The maximum number of resources returned in the response.'),
        'offset': fields.Integer(required=False,
                                 description='The offset of the first resource returned in the response.'),
    },
)

