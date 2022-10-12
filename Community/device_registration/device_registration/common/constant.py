# Copyright 2022 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = '../config/config.ini'
CONFIG_PATH_FOR_CREDENTIAL = os.path.abspath(os.path.join(cur_dir, '..', 'config/config.ini'))
DEPLOY_PROPERTIES = 'scope={scope}|batchMode={batch}'.format(scope='related', batch='batch_By_Server')


class DefaultConfiguration:
    CONFIG_NAME = 'test_config'
    VIEW_NAME = 'default'


class Device:
    Group = "device_group"
    Location = "device_location"
    Network = "device_network"
    Domain = "dns_domain"
    Mac_address = "mac_address"
    Ip_address = "ip_address"
    Name = "name"
    Host_name = "device_host_name"
    Host_id = "host_record_id"
    Account_id = "account_id"
    Description = "description"
    Audit = "audit"
    Access_right = "access_right"
    Device_id = 'device_id'
    View = 'view'
    Domain_name = 'domain'
    Ip_address_id = 'ip_address_id'
    Ip_info = 'ip_info'
    Host_record_name = 'host_name'
    IS_MULTIPLE_IP = 'is_multiple_ip'


class DeviceProperties:
    Account_id = "mac-account-id"
    Description = "mac-description"
    Address = "address"
    Audit = "mac-audit-trail"
    Location = "mac-location"

class DeviceAudit:
    User = "user"
    Action = "action"
    DateTime = "date_time"

class DeviceAction:
    CREATE = "create"
    UPDATE = "update"

class AccessRight:
    HIDE = "HIDE"
    VIEW = "VIEW"
    ADD = "ADD"
    CHANGE = "CHANGE"
    FULL_ACCESS = "FULL"


class Preference:
    TRUE = 'true'
    FALSE = 'false'


class NetworkItem:
    NETWORKITEM = "IP4Network"
    NAME = "name"
    DETAIL = "detail"
    NEXT_IP = "next_ip" 


class DnsItem:
    DNSITEM = "DNS_domain"


class LocationItem:
    LOCATIONITEM = "Location_name"


class UDF:
    LOCATIONCODE = "zone-location-code"
    PREFERENCE = 'preference'


class UserType:
    TYPE = "userType"
    ADMIN = "ADMIN"
    REGULAR = "REGULAR"
    USERNAME = "username"
    PASSWORD = "password"


class CONFIG:
    ADMIN_USERNAME = "ADMIN_USERNAME"
    ADMIN_PASSWORD = "ADMIN_PASSWORD"
    BAM_CONFIG = "BAM_CONFIG"


class PROPERTY:
    ABS_NAME = "absoluteName"
    LOCATION_CODE = "locationCode"
    CIDR = "CIDR"


class DEFAULT_COUNT:
    DEFAULT_MAX_COUNT = 10000
