# Copyright 2022 BlueCat Networks. All rights reserved.
from flask_restplus import reqparse

mac_address_parser = reqparse.RequestParser()
mac_address_parser.add_argument('mac_address', location="json", required=True, help='The MAC address of the device')
mac_address_parser.add_argument('name', location="json", required=True, help='The name of the device')
mac_address_parser.add_argument('device_group', location="json", required=True, help='The tagged group of the device')
mac_address_parser.add_argument('device_location', location="json", help='The location of the device', default='')
mac_address_parser.add_argument('ip_address', location="json", help='The IP network of the device', default='')
mac_address_parser.add_argument('dns_domain', location="json", help='The DNS domain of the device', default='')
mac_address_parser.add_argument('account_id', location="json", help='The account ID of the device', default='')
mac_address_parser.add_argument('description', location="json", help='The description of the device', default='')
mac_address_parser.add_argument('access_right', location="json", help='The user access right', default='')

mac_address_meta_update_parser = reqparse.RequestParser()
mac_address_meta_update_parser.add_argument('mac_address', location="json", required=True,
                                            help='The MAC address of the device')
mac_address_meta_update_parser.add_argument('name', location="json", required=True, help='The name of the device')
mac_address_meta_update_parser.add_argument('ip_address_id', location="json", help='The ID of the device IP address', default='')
mac_address_meta_update_parser.add_argument('host_record_id', location="json", help='The ID of the device host record', default='')
mac_address_meta_update_parser.add_argument('account_id', location="json", help='The account ID of the device', default='')
mac_address_meta_update_parser.add_argument('description', location="json", help='The description of the device', default='')
mac_address_meta_update_parser.add_argument('access_right', location="json", help='The user access right', default='')
