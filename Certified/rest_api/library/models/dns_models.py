# Copyright 2020 BlueCat Networks. All rights reserved.

from flask_restplus import fields

from main_app import api
from .configuration_models import entity_model

zone_model = api.clone(
    'zones',
    entity_model
)

view_model = api.clone(
    'views',
    entity_model
)

external_host_model = api.model(
    'external_host_records',
    {
        'absolute_name': fields.String(required=True, description='The FQDN of the external host record')
    },
)

host_model = api.model(
    'host_records',
    {
        'absolute_name': fields.String(required=True, description='The FQDN of the host record'),
        'ip4_address': fields.String(description='The IPv4 addresses associated with the host record'),
        'ttl': fields.Integer(description='The TTL of the host record'),
        'properties': fields.String(description='The properties of the host record', default='attribute=value|'),
    },
)

host_patch_model = api.model(
    'host_records_patch',
    {
        'name': fields.String(description='The name of the host record'),
        'ip4_address': fields.String(description='The IPv4 addresses associated with the host record'),
        'ttl': fields.Integer(description='The TTL of the host record'),
        'properties': fields.String(description='The properties of the host record', default='attribute=value|'),
    },
)

cname_model = api.model(
    'cname_records',
    {
        'absolute_name': fields.String(required=True, description='The FQDN of the CName record'),
        'linked_record': fields.String(
            required=True,
            description='The name of the record to which this alias will link',
        ),
        'ttl': fields.Integer(description='The TTL of the CName record'),
        'properties': fields.String(description='The properties of the CName record', default='attribute=value|'),
    },
)

cname_patch_model = api.model(
    'cname_records_patch',
    {
        'name': fields.String(description='The name of the alias record'),
        'linked_record': fields.String(description='The name of the record to which this alias will link'),
        'ttl': fields.Integer(description='The TTL of the CName record'),
        'properties': fields.String(description='The properties of the CName record', default='attribute=value|'),
    },
)
