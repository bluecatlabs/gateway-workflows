# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
from bluecat.entity import Entity

DEFAULT_FIELDS = 'id,name,type'
ALLOW_TARGET_COLLECTION = 'zones/interfaces/bocks/networks'
enable_copy_dns_option = True


class Constants:
    @classmethod
    def all(cls):
        return [value for name, value in vars(cls).items() if name.isupper()]


class Actions(Constants):
    COPY = 'copy'
    MOVE = 'move'
    MOVE_PRIMARY = 'movePrimary'
    ADD_SERVERS = 'addServers'
    EXPOSE = 'expose'
    HIDE = 'hide'
    DELETE = 'delete'


class ActionOption(Constants):
    ACTION = 'action'
    VALIDATE = 'validate'
    MIGRATE = 'migrate'


class EntityV2(Constants):
    CONFIGURATION = Entity.Configuration
    VIEW = Entity.View
    ZONE = Entity.Zone
    IP4_NETWORK = 'IPv4Network'
    IP4_BLOCK = 'IPv4Block'
    IP6_NETWORK = 'IPv6Network'
    IP6_BLOCK = 'IPv6Block'
    SERVER = Entity.Server
    SERVER_GROUP = 'ServerGroup'
    DNS_OPTION = Entity.DNSOption
    DNS_ROLE = Entity.DeploymentRole
    NETWORK_INTERFACE = 'NetworkInterface'

    @classmethod
    def get_collection(cls, data):
        code_mapping = {
            cls.CONFIGURATION: Collections.CONFIGURATIONS,
            cls.VIEW: Collections.VIEWS,
            cls.ZONE: Collections.ZONES,
            cls.SERVER: Collections.SERVERS,
            cls.IP4_NETWORK: Collections.NETWORKS,
            cls.IP4_BLOCK: Collections.BLOCKS,
            cls.IP6_NETWORK: Collections.NETWORKS,
            cls.IP6_BLOCK: Collections.BLOCKS,
        }
        return code_mapping.get(data, '')

    @classmethod
    def get_migration_key(cls, data):
        code_mapping = {
            cls.CONFIGURATION: 'configuration',
            cls.VIEW: 'view',
            cls.ZONE: 'zone',
            cls.SERVER: 'server',
            cls.IP4_NETWORK: 'ip4-network',
            cls.IP4_BLOCK: 'ip4-block',
            cls.IP6_NETWORK: 'ip6-network',
            cls.IP6_BLOCK: 'ip6-block',
            cls.DNS_OPTION: 'dns-option',
            cls.DNS_ROLE: 'dns-role',
        }
        return code_mapping.get(data, '')


class Collections(Constants):
    SERVERS = "servers"
    BLOCKS = "blocks"
    NETWORKS = "networks"
    VIEWS = "views"
    ZONES = "zones"
    DEPLOYMENT_OPTIONS = 'deploymentOptions'
    INTERFACES = 'interfaces'
    CONFIGURATIONS = 'configurations'

    @classmethod
    def get_entity_type(cls, data):
        code_mapping = {
            cls.CONFIGURATIONS: Entity.Configuration,
            cls.SERVERS: Entity.Server,
            cls.BLOCKS: EntityV2.IP4_BLOCK,
            cls.VIEWS: Entity.View,
            cls.ZONES: Entity.Zone,
            cls.NETWORKS: EntityV2.IP4_NETWORK,
            cls.INTERFACES: Entity.NetworkInterface
        }
        return code_mapping.get(data, '')


class GroupOption(Constants):
    BY_PARENT = 'parentEntity'
    BY_SERVER = 'serverInterface'
    BY_ROLE = 'roleType'
    BY_ROLE_SERVER = 'roleServer'
    ALL_ROLES = 'allRoles'


class RoleType(Constants):
    PRIMARY = 'PRIMARY'
    HIDDEN_PRIMARY = 'HIDDEN_PRIMARY'
    SECONDARY = 'SECONDARY'
    STEALTH_SECONDARY = 'STEALTH_SECONDARY'
    FORWARDER = 'FORWARDING'
    STUB = 'STUB'
    NONE = 'NONE'
    RECURSION = 'RECURSION'


# role groups
SECONDARY_GROUP = [RoleType.SECONDARY, RoleType.STEALTH_SECONDARY]
PRIMARY_GROUP = [RoleType.PRIMARY, RoleType.HIDDEN_PRIMARY]
EXPOSE_ROLES = [RoleType.PRIMARY, RoleType.SECONDARY]
HIDE_ROLES = [RoleType.HIDDEN_PRIMARY, RoleType.STEALTH_SECONDARY]
AUTHORITATIVE_ROLES = [RoleType.PRIMARY, RoleType.HIDDEN_PRIMARY, RoleType.SECONDARY, RoleType.STEALTH_SECONDARY]
RECURSIVE_ROLES = [RoleType.STUB, RoleType.FORWARDER]


class RoleGroup(Constants):
    ALL = 'allRoles'
    PRIMARY = 'primaryRoles'
    EXPOSED = 'exposedRoles'
    AUTHORITATIVE = 'authoritativeRoles'
    RECURSION = 'recursionRoles'
    FORWARDING = 'forwardingRoles'

    @classmethod
    def get_roles(cls, data):
        code_mapping = {
            cls.ALL: RoleType.all(),
            cls.PRIMARY: [RoleType.PRIMARY, RoleType.HIDDEN_PRIMARY],
            cls.EXPOSED: [RoleType.PRIMARY, RoleType.SECONDARY],
            cls.AUTHORITATIVE: [RoleType.PRIMARY, RoleType.HIDDEN_PRIMARY] + SECONDARY_GROUP,
            cls.RECURSION: [RoleType.STUB, RoleType.FORWARDER],
            cls.FORWARDING: [RoleType.FORWARDER],
        }
        return code_mapping.get(data, '')


class ZoneTypeCls:
    REVERSE_ZONE = [Collections.BLOCKS, Collections.NETWORKS]
    FORWARDER_ZONE = [Collections.ZONES, Collections.VIEWS]


class ZoneType:
    REVERSE_ZONE = [EntityV2.IP6_BLOCK, EntityV2.IP4_BLOCK, EntityV2.IP4_NETWORK, EntityV2.IP6_NETWORK]
    FORWARDER_ZONE = [EntityV2.VIEW, EntityV2.ZONE]
