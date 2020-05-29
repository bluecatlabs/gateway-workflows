# Copyright 2020 BlueCat Networks. All rights reserved.

from flask_restplus import reqparse

block_post_parser = reqparse.RequestParser()
block_post_parser.add_argument('name', location="json", help='The name associated with the IP4 Block.')
block_post_parser.add_argument('address', location="json", help='The address associated with the IP4 Block.')
block_post_parser.add_argument(
    'cidr_notation', location="json", help='The block CIDR notation expressed as a value of 8-31'
)
block_post_parser.add_argument('properties', location="json", help='The properties of the IP4 Block')

network_patch_parser = reqparse.RequestParser()
network_patch_parser.add_argument('name', location="json", help='The name of the network')
network_patch_parser.add_argument('properties', location="json", help='The properties of the record')

network_post_parser = reqparse.RequestParser()
network_post_parser.add_argument('name', location="json", help='The name of the network')
network_post_parser.add_argument('properties', location="json", help='The properties of the network')
network_post_parser.add_argument(
    'size',
    location="json",
    help='The number of addresses in the network expressed as a power of 2 (i.e. 2, 4, 8, 16, ... 256)'
)

network_add_parser = reqparse.RequestParser()
network_add_parser.add_argument('cidr', location="json", help='The CIDR notation of the network')
network_add_parser.add_argument('properties', location="json", help='The properties of the network')

ip4_address_post_parser = reqparse.RequestParser()
ip4_address_post_parser.add_argument('mac_address', location="json", help='The MAC address')
ip4_address_post_parser.add_argument('hostinfo', location="json", help='The hostinfo of the address')
ip4_address_post_parser.add_argument('action', location="json", help='The action for address assignment')
ip4_address_post_parser.add_argument('properties', location="json", help='The properties of the record')

ip4_address_patch_parser = reqparse.RequestParser()
ip4_address_patch_parser.add_argument('mac_address', location="json", help='The MAC address')
ip4_address_patch_parser.add_argument('action', location="json", help='The action for address assignment')
ip4_address_patch_parser.add_argument('properties', location="json", help='The properties of the record')
