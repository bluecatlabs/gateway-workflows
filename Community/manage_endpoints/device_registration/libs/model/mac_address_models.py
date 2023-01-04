# Copyright 2022 BlueCat Networks. All rights reserved.
from flask_restplus import fields

from main_app import api

mac_address_model = api.clone(
    'mac_address',
    {
        'mac_address': fields.String(required=True, description='The mac address of device'),
        'name': fields.String(description='The name of device'),
        'device_group': fields.String(required=True, description='The name of device type'),
        'device_location': fields.String(description='The name of device subtype'),
        'ip_address': fields.String(description='The IPv4 address associated with device'),
        'dns_domain': fields.String(description='The DNS Domain of the device'),
        'account_id': fields.String(description='The properties of device'),
        'description': fields.String(description='The properties of device'),
        'access_right': fields.String(description='The user access right'),
    }
)

mac_address_meta_update_model = api.clone(
    'mac_address_update',
    {
        'mac_address': fields.String(required=True, description='The mac address of device'),
        'name': fields.String(description='The name of device'),
        'ip_address_id': fields.String(description='The ID of device ip address'),
        'host_record_id': fields.String(description='The ID of device host record'),
        'account_id': fields.String(description='The account ID of device'),
        'description': fields.String(description='The description of device'),
        'access_right': fields.String(description='The user access right'),
    }
)
