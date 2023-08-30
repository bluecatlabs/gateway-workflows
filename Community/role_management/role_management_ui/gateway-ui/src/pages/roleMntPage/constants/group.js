import {
    GROUP_ROLE_COLUMNS,
    GROUP_ROLE_SERVER_COLUMNS,
    GROUP_SERVER_COLUMNS,
    GROUP_ZONE_COLUMNS,
} from './table';

export const GROUPBY_OPTIONS = [
    { value: null, label: 'None' },
    { value: 'zone', label: 'Zone' },
    { value: 'role', label: 'Role' },
    { value: 'server', label: 'Server' },
    { value: 'role_server', label: 'Role of Server' },
];

export const GROUP_TO_COLUMNS = {
    zone: GROUP_ZONE_COLUMNS,
    role: GROUP_ROLE_COLUMNS,
    server: GROUP_SERVER_COLUMNS,
    role_server: GROUP_ROLE_SERVER_COLUMNS,
};
