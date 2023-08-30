export const FILTER_MENU_OPTIONS = ['zone', 'reverseZone', 'interfaceList', 'role'];

export const FILTER_LABELS = {
    interfaceList: 'Server Interface',
    zone: 'Zone',
    reverseZone: 'Reverse Zone',
    role: 'Role',
    group_role: 'Roles Group',
    custom_role: 'Roles',
};

export const ROLE_OPTION_LABELS = {
    group_role: 'Roles Group',
    custom_role: 'Roles',
};

export const ROLE_OPTIONS = [
    { value: 'PRIMARY', label: 'Primary' },
    { value: 'HIDDEN_PRIMARY', label: 'Hidden Primary' },
    { value: 'SECONDARY', label: 'Secondary' },
    { value: 'STEALTH_SECONDARY', label: 'Stealth Secondary' },
    { value: 'STUB', label: 'Stub' },
    { value: 'FORWARDING', label: 'Forwarder' },
    { value: 'RECURSION', label: 'Recursion' },
    { value: 'NONE', label: 'None' },
];

export const GROUP_ROLE_LABELS = {
    allRoles: 'All roles',
    primaryRoles: 'Primary roles',
    exposedRoles: 'Exposed roles',
    authoritativeRoles: 'Authoritative roles',
    recursionRoles: 'Recursion roles',
    forwardingRoles: 'Forwarding roles',
};

export const INHERIT_OPTIONS = [
    {
        value: false,
        label: 'No',
    },
    {
        value: true,
        label: 'Yes',
    },
];
