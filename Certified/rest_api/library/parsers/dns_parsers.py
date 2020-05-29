# Copyright 2020 BlueCat Networks. All rights reserved.

from flask_restplus import reqparse

host_parser = reqparse.RequestParser()
host_parser.add_argument('absolute_name', location="json", required=True, help='The FQDN of the record')
host_parser.add_argument(
    'ip4_address',
    location="json",
    required=True,
    help='The IPv4 addresses associated with the host record',
)
host_parser.add_argument('ttl', type=int, location="json", help='The TTL of the record')
host_parser.add_argument('properties', location="json", help='The properties of the record')

host_patch_parser = host_parser.copy()
host_patch_parser.replace_argument(
    'ip4_address',
    location="json",
    required=False,
    help='The IPv4 addresses associated with the host record',
)
host_patch_parser.add_argument('name', location="json", help='The name of the record')
host_patch_parser.remove_argument('absolute_name')

cname_parser = host_parser.copy()
cname_parser.remove_argument('ip4_address')
cname_parser.add_argument('linked_record', location="json", help='The name of the record to which this alias will link')

cname_patch_parser = cname_parser.copy()
cname_patch_parser.add_argument('name', location="json", help='The name of the alias record')
cname_patch_parser.remove_argument('absolute_name')

external_host_parser = host_parser.copy()
external_host_parser.remove_argument('ip4_address')
external_host_parser.remove_argument('properties')
external_host_parser.remove_argument('ttl')
