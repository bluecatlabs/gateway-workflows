export const ACTION_NAMES = {
    COPY_ROLES_TO_SERVER: 'COPY_ROLES_TO_SERVER',
    MOVE_ROLES_TO_SERVER: 'MOVE_ROLES_TO_SERVER',
    COPY_ROLES_TO_ZONES: 'COPY_ROLES_TO_ZONES',
    EXPOSE_ROLES: 'EXPOSE_ROLES',
    HIDE_ROLES: 'HIDE_ROLES',
    DELETE_ROLES: 'DELETE_ROLES',
    ADD_SERVERS: 'ADD_SERVERS',
    MOVE_PRIMARY_ROLE: 'MOVE_PRIMARY_ROLE',
};

export const ACTION_TYPES = {
    COPY_ROLES_TO_SERVER: 0,
    MOVE_ROLES_TO_SERVER: 0,
    COPY_ROLES_TO_ZONES: 0,
    EXPOSE_ROLES: 0,
    HIDE_ROLES: 0,
    DELETE_ROLES: 0,
    ADD_SERVERS: 1,
    MOVE_PRIMARY_ROLE: 1,
};

export const ROLE_ACTIONS = [
    {
        name: ACTION_NAMES.COPY_ROLES_TO_SERVER,
        text: 'Copy Roles To Server',
        actionText: 'Copy Roles',
    },
    {
        name: ACTION_NAMES.MOVE_ROLES_TO_SERVER,
        text: 'Move Roles To Server',
        actionText: 'Move Roles',
    },
    {
        name: ACTION_NAMES.COPY_ROLES_TO_ZONES,
        text: 'Copy Roles To Zones',
        actionText: 'Copy Roles',
    },
    { name: ACTION_NAMES.EXPOSE_ROLES, text: 'Expose Roles', actionText: 'Expose' },
    { name: ACTION_NAMES.HIDE_ROLES, text: 'Hide Roles', actionText: 'Hide' },
    { name: ACTION_NAMES.DELETE_ROLES, text: 'Delete Roles', actionText: 'Delete' },
];

export const ZONE_ROLE_ACTIONS = [
    ...ROLE_ACTIONS,
    {
        name: ACTION_NAMES.MOVE_PRIMARY_ROLE,
        text: 'Move Primary Role',
        actionText: 'Move',
    },
    { name: ACTION_NAMES.ADD_SERVERS, text: 'Add Server Roles', actionText: 'Add' },
];

export const ROLE_TYPE_LABELS = {
    'PRIMARY': 'Primary',
    'HIDDEN_PRIMARY': 'Hidden Primary',
    'SECONDARY': 'Secondary',
    'STEALTH_SECONDARY': 'Stealth Secondary',
    'STUB': 'Stub',
    'FORWARDING': 'Forwarder',
    'RECURSION': 'Recursion',
    'NONE': 'None',
};

export const ADD_SERVERS_ROLE_TYPE_OPTIONS = [
    { value: 'SECONDARY', label: 'Secondary' },
    { value: 'STEALTH_SECONDARY', label: 'Stealth Secondary' },
    { value: 'STUB', label: 'Stub' },
    { value: 'FORWARDING', label: 'Forwarder' },
];

export const ACTION_NAME_TO_API_PARAM = {
    [ACTION_NAMES.HIDE_ROLES]: 'hide',
    [ACTION_NAMES.DELETE_ROLES]: 'delete',
    [ACTION_NAMES.EXPOSE_ROLES]: 'expose',
    [ACTION_NAMES.COPY_ROLES_TO_ZONES]: 'copy',
    [ACTION_NAMES.COPY_ROLES_TO_SERVER]: 'copy',
    [ACTION_NAMES.MOVE_ROLES_TO_SERVER]: 'move',
    [ACTION_NAMES.ADD_SERVERS]: 'addServers',
    [ACTION_NAMES.MOVE_PRIMARY_ROLE]: 'movePrimary',
};
