# Copyright 2020 BlueCat Networks. All rights reserved.

from flask_restplus import fields

from main_app import api

entity_model = api.model(
    'entities',
    {
        'name': fields.String(description='The name of the entity.'),
        'properties': fields.String(
            description='The properties of the entity in the following format:key=value|key=value|'
        ),
    },
)

entity_return_model = api.model(
    'Entity Object',
    {
        'id': fields.Integer(description='ID of the entity.'),
        'name': fields.String(description='The name of the entity.'),
        'type': fields.String(description='The type of the entity.'),
        'properties': fields.String(
            description='The properties of the entity in the following format:key=value|key=value|'
        ),
    },
)
