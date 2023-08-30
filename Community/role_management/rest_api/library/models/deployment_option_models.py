# Copyright 2023 BlueCat Networks. All rights reserved.

from flask_restx import fields

from .... import bp_rm

deployment_option_model = bp_rm.model(
    'deployment_option',
    {
        'collection': fields.String(required=True, description='The collection resource'),
        'collection_name': fields.String(required=True, description='The Name of the collection resource'),
    },
)

create_deployment_option_model = bp_rm.model(
    'create_deployment_option',
    {
        'options': fields.List(fields.Raw, required=True, example=[{
            "name": "forwarding",
            "type": "DNSOption",
            "value": [
                "no",
                "192.168.88.89"
            ]
        }])
    },
)

delete_deployment_option_model = bp_rm.model(
    'delete_deployment_option',
    {
        'ids': fields.List(fields.Integer, required=True, example=[123, 456])
    },
)
