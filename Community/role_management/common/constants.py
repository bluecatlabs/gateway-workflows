# Copyright 2023 BlueCat Networks. All rights reserved.
import os


def get_default_config():
    config_path = os.path.join(BLUECAT_GATEWAY_CONFIG, 'config.ini')
    if not os.path.isfile(config_path):
        config_path = os.path.join(DEFAULT_CONFIG, 'config.ini')
    return config_path


BLUECAT_GATEWAY_CONFIG = "/bluecat_gateway/workflows/role_management/config/"
cur_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(cur_dir, "../config")
MIGRATION_PATH = os.path.abspath(os.path.join(cur_dir, os.pardir)) + '/migrations'
MIGRATION_CONFIG = cur_dir + '/../config/migration.ini'
MAX_FILE_STORE = 5


class Constants:
    @classmethod
    def all(cls):
        return [value for name, value in vars(cls).items() if name.isupper()]


class OnExist:
    SKIP_OBJECT = 'skip-object'
    SKIP_TREE = 'skip-tree'
    MERGE_OBJECT = 'merge-object'
    DELETE_TREE = 'delete-tree'
    UNLINK = 'unlink'
    RECREATE_TREE = 'recreate-tree'


class OpType:
    REMARK = "remark"
    CONFIG = "configuration"
    VIEW = "view"
    RECORD = "record"
    ZONE = "zone"
    IP4_BLOCK = "ip4-block"
    IP4_NETWORK = "ip4-network"
    IP6_BLOCK = "ip6-block"
    IP6_NETWORK = "ip6-network"
    DNS_ROLE = "dns-role"
    DNS_OPTION = "dns-option"
    OPTION_VALUE = "option-value"


class ServerDeploymentStatus(Constants):
    EXECUTING = -1
    INITIALIZING = 0
    QUEUED = 1
    CANCELLED = 2
    FAILED = 3
    NOT_DEPLOYED = 4
    WARNING = 5
    INVALID = 6
    DONE = 7
    NO_RECENT_DEPLOYMENT = 8
    CANCELLING = 9

    @classmethod
    def get_status(cls, data):
        code_mapping = {
            cls.EXECUTING: 'Executing',
            cls.INITIALIZING: 'Initializing',
            cls.QUEUED: 'Queued',
            cls.CANCELLED: 'Cancelled',
            cls.FAILED: 'Failed',
            cls.NOT_DEPLOYED: 'Not Deployed',
            cls.WARNING: 'Warning',
            cls.INVALID: 'Invalid',
            cls.DONE: 'Done',
            cls.NO_RECENT_DEPLOYMENT: 'No Recent Deployment',
            cls.CANCELLING: 'Canceling'
        }
        return code_mapping.get(data, '')

    @classmethod
    def get_success_status(cls):
        return [2, 3, 4, 5, 6, 7, 8]


class Status(Constants):
    DUPLICATED = 'DUPLICATED'
    CONFLICTED = 'CONFLICTED'
    AVAILABLE = 'AVAILABLE'
    UNAVAILABLE = 'UNAVAILABLE'
    INFO = 'INFO'
    SUCCESSFULLY = 'SUCCESSFULLY'
    FAILED = 'FAILED'
    WARNING = 'WARNING'


class DNSDeploymentRoles(Constants):
    NONE = 'NONE'
    MASTER = 'PRIMARY'
    MASTER_HIDDEN = 'PRIMARY_HIDDEN'
    HIDDEN_PRIMARY = 'HIDDEN_PRIMARY'
    SLAVE = 'SECONDARY'
    SLAVE_STEALTH = 'SECONDARY_STEALTH'
    STEALTH_SECONDARY = 'STEALTH_SECONDARY'
    FORWARDER = 'FORWARDING'
    STUB = 'STUB'
    RECURSION = 'RECURSION'
    AD_MASTER = 'AD_PRIMARY'

    @classmethod
    def get_migration_type(cls, role):
        code_mapping = {
            cls.NONE: 'none',
            cls.MASTER: 'master',
            cls.MASTER_HIDDEN: 'hidden-master',
            cls.HIDDEN_PRIMARY: 'hidden-master',
            cls.SLAVE: 'slave',
            cls.SLAVE_STEALTH: 'stealth-slave',
            cls.STEALTH_SECONDARY: 'stealth-slave',
            cls.FORWARDER: 'forwarding',
            cls.RECURSION: 'recursion',
            cls.STUB: 'stub',
            cls.AD_MASTER: 'ad-master'
        }
        return code_mapping.get(role, '')


class DeploymentRoleInterfaceType(Constants):
    SERVICE = 'SERVICE'
    ZONE_TRANSFER = 'ZONE_TRANSFER'
    TARGET = 'TARGET'
    ZONE_TRANSFER_TYPES = [ZONE_TRANSFER, TARGET]
