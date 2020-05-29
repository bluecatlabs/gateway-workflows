# Copyright 2020 BlueCat Networks. All rights reserved.

from flask_restplus import fields

from main_app import api

ip4_address_post_model = api.model(
    'ipv4_address',
    {
        'mac_address': fields.String(description='MAC Address value'),
        'hostinfo': fields.String(
            description='A string containing host information for the address in the following format: '
                        'hostname,viewId,reverseFlag,sameAsZoneFlag'
        ),
        'action': fields.String(
            description='Desired IP4 address state: MAKE_STATIC / MAKE_RESERVED / MAKE_DHCP_RESERVED'
        ),
        'properties': fields.String(description='The properties of the IP4 Address', default='attribute=value|'),
    },
)

next_ip4_address_post_model = api.clone(
    'get_next_ip',
    ip4_address_post_model
)

ip4_address_patch_model = api.model(
    'ip4_address_patch',
    {
        'mac_address': fields.String(description='MAC Address value'),
        'action': fields.String(
            description='Desired IP4 address state: MAKE_STATIC / MAKE_RESERVED / MAKE_DHCP_RESERVED'
        ),
        'properties': fields.String(description='The properties of the IP4 Address', default='attribute=value|'),
    },
)

network_patch_model = api.model(
    'ipv4_networks_patch',
    {
        'name': fields.String(description='The name associated with the IP4 Network.'),
        'properties': fields.String(description='The properties of the IP4 Network', default='attribute=value|'),
    },
)

network_post_model = api.model(
    'ipv4_networks_post',
    {
        'name': fields.String(description='The name associated with the IP4 Network.'),
        'size': fields.String(
            description='The number of addresses in the network expressed as a power of 2 (i.e. 2, 4, 8, 16, ... 256)',
            default='attribute=value|'
        ),
        'properties': fields.String(description='The properties of the IP4 Network', default='attribute=value|'),
    },
)

network_add_model = api.model(
    'create_network',
    {
        'cidr': fields.String(required=True, description='The CIDR notation for the network'),
        'properties': fields.String(description='The properties of the IP4 Network', default='attribute=value|'),
    },
)

block_post_model = api.model(
    'ipv4_block_post',
    {
        'name': fields.String(description='The name associated with the IP4 Block.'),
        'address': fields.String(description='The address associated with the IP4 Block.'),
        'cidr_notation': fields.String(description='The block CIDR notation expressed as a value of 8-31'),
        'properties': fields.String(description='The properties of the IP4 Block', default='attribute=value|'),
    },
)
