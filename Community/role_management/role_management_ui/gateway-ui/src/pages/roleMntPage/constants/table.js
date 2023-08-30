import { stringCompare } from '../../../utils/common';
import Icon from '../components/icons/Icon';
import StatusIcon from '../components/icons/StatusIcon';
import CellContentWrapper from '../components/table/CellContentWrapper';
import CellWrapper from '../components/table/CellWrapper';
import SkeletonCell from '../components/table/SkeletonCell';

const PAGE_SIZE = 20;

const DEFAULT_COLUMNS = [
    {
        id: 'zone',
        header: 'Zone',
        value: (item) => {
            return (
                <CellWrapper hasIcon={true}>
                    <Icon type={item.zoneType || 'View'} size='small' />
                    {item.zone ? (
                        <CellContentWrapper content={`${item.zone} [${item.view}]`} />
                    ) : (
                        <CellContentWrapper content={item.view} />
                    )}
                </CellWrapper>
            );
        },
        comparator: (a, b) => stringCompare(a.zone, b.zone),
        style: { width: '35%' },
    },
    {
        id: 'server',
        header: 'Server Interface',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.server} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.server, b.server),
        style: { width: '20%' },
    },
    {
        id: 'role',
        header: 'Role',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.role} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.role, b.role),
        style: { width: '20%' },
    },
    {
        id: 'transfer',
        header: 'Zone Transfer Interface',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.transfer} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.transfer, b.transfer),
        style: { width: '25%' },
    },
];

const INHERIT_COLUMN = {
    id: 'inherit',
    header: 'Inherited From',
    value: (item) => {
        const name = item.inheritedFrom?.name || item.inheritedFrom?.reverseZoneName;
        return (
            <CellWrapper>
                {name && <Icon type={item.inheritedFrom?.type || 'View'} size='small' />}
                <CellContentWrapper content={name} />
            </CellWrapper>
        );
    },
    comparator: (a, b) => {
        const compareString = (o) =>
            o.inheritedFrom?.type + (o.inheritedFrom?.name || o.inheritedFrom?.reverseZoneName);
        return stringCompare(compareString(a), compareString(b));
    },
};

const DEFAULT_COLUMNS_WITH_INHERIT = [
    {
        id: 'zone',
        header: 'Zone',
        value: (item) => {
            return (
                <CellWrapper hasIcon={true}>
                    <Icon type={item.zoneType || 'View'} size='small' />
                    {item.zone ? (
                        <CellContentWrapper content={`${item.zone} [${item.view}]`} />
                    ) : (
                        <CellContentWrapper content={item.view} />
                    )}
                </CellWrapper>
            );
        },
        comparator: (a, b) => stringCompare(a.zone, b.zone),
        style: { width: '30%' },
    },
    {
        id: 'server',
        header: 'Server Interface',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.server} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.server, b.server),
        style: { width: '20%' },
    },
    {
        id: 'role',
        header: 'Role',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.role} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.role, b.role),
        style: { width: '20%' },
    },
    {
        id: 'transfer',
        header: 'Zone Transfer Interface',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.transfer} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.transfer, b.transfer),
        style: { width: '15%' },
    },
    INHERIT_COLUMN,
];

const DETAIL_NO_GROUP_COLUMNS = [
    {
        id: 'zone',
        header: 'Zone',
        value: (item) => {
            return (
                <CellWrapper hasIcon={true}>
                    <Icon type={item.zoneType || 'View'} size='small' />
                    {item.zone ? (
                        <CellContentWrapper content={`${item.zone} [${item.view}]`} />
                    ) : (
                        <CellContentWrapper content={item.view} />
                    )}
                </CellWrapper>
            );
        },
        comparator: (a, b) => stringCompare(a.zone, b.zone),
        style: { width: '25%' },
    },
    {
        id: 'server',
        header: 'Server Interface',
        value: (item) => {
            if (!item.parentServer) return <CellWrapper skeleton={true} />;
            return (
                <CellWrapper>
                    <CellContentWrapper
                        content={
                            item.parentServer ? (
                                `${item.parentServer} [${item.server}]`
                            ) : (
                                <SkeletonCell />
                            )
                        }
                    />
                </CellWrapper>
            );
        },
        comparator: (a, b) => stringCompare(a.server, b.server),
        style: { width: '30%' },
    },
    {
        id: 'role',
        header: 'Role',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.role} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.role, b.role),
        style: { width: '15%' },
    },
    {
        id: 'transfer',
        header: 'Zone Transfer Interface',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.transfer} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.transfer, b.transfer),
        style: { width: '15%' },
    },
];

const DETAIL_NO_GROUP_COLUMNS_WITH_INHERIT = [...DETAIL_NO_GROUP_COLUMNS, INHERIT_COLUMN];

const DETAIL_ZONE_GROUP_COLUMNS = [
    {
        id: 'server',
        header: 'Server Interface',
        value: (item) => {
            if (!item.parentServer) return <CellWrapper skeleton={true} />;
            return (
                <CellWrapper>
                    <CellContentWrapper
                        content={
                            item.parentServer ? (
                                `${item.parentServer} [${item.server}]`
                            ) : (
                                <SkeletonCell />
                            )
                        }
                    />
                </CellWrapper>
            );
        },
        comparator: (a, b) => stringCompare(a.server, b.server),
        style: { width: '25%' },
    },
    {
        id: 'role',
        header: 'Role',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.role} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.role, b.role),
        style: { width: '25%' },
    },
    {
        id: 'transfer',
        header: 'Zone Transfer Interface',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.transfer} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.transfer, b.transfer),
        style: { width: '25%' },
    },
];
const DETAIL_ZONE_GROUP_COLUMNS_WITH_INHERIT = [...DETAIL_ZONE_GROUP_COLUMNS, INHERIT_COLUMN];

const DETAIL_ROLE_GROUP_COLUMNS = [
    {
        id: 'zone',
        header: 'Zone',
        value: (item) => {
            return (
                <CellWrapper hasIcon={true}>
                    <Icon type={item.zoneType || 'View'} size='small' />
                    {item.zone ? (
                        <CellContentWrapper content={`${item.zone} [${item.view}]`} />
                    ) : (
                        <CellContentWrapper content={item.view} />
                    )}
                </CellWrapper>
            );
        },
        comparator: (a, b) => stringCompare(a.zone, b.zone),
        style: { width: '30%' },
    },
    {
        id: 'server',
        header: 'Server Interface',
        value: (item) => {
            if (!item.parentServer) return <CellWrapper skeleton={true} />;
            return (
                <CellWrapper>
                    <CellContentWrapper
                        content={
                            item.parentServer ? (
                                `${item.parentServer} [${item.server}]`
                            ) : (
                                <SkeletonCell />
                            )
                        }
                    />
                </CellWrapper>
            );
        },
        comparator: (a, b) => stringCompare(a.server, b.server),
        style: { width: '30%' },
    },
    {
        id: 'transfer',
        header: 'Zone Transfer Interface',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.transfer} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.transfer, b.transfer),
        style: { width: '20%' },
    },
];
const DETAIL_ROLE_GROUP_COLUMNS_WITH_INHERIT = [...DETAIL_ROLE_GROUP_COLUMNS, INHERIT_COLUMN];

const DETAIL_SERVER_GROUP_COLUMNS = [
    {
        id: 'zone',
        header: 'Zone',
        value: (item) => {
            return (
                <CellWrapper hasIcon={true}>
                    <Icon type={item.zoneType || 'View'} size='small' />
                    {item.zone ? (
                        <CellContentWrapper content={`${item.zone} [${item.view}]`} />
                    ) : (
                        <CellContentWrapper content={item.view} />
                    )}
                </CellWrapper>
            );
        },
        comparator: (a, b) => stringCompare(a.zone, b.zone),
        style: { width: '40%' },
    },
    {
        id: 'role',
        header: 'Role',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.role} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.role, b.role),
        style: { width: '20%' },
    },
    {
        id: 'transfer',
        header: 'Zone Transfer Interface',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.transfer} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.transfer, b.transfer),
        style: { width: '20%' },
    },
];
const DETAIL_SERVER_GROUP_COLUMNS_WITH_INHERIT = [...DETAIL_SERVER_GROUP_COLUMNS, INHERIT_COLUMN];

const DETAIL_ROLE_SERVER_GROUP_COLUMNS = [
    {
        id: 'zone',
        header: 'Zone',
        value: (item) => {
            return (
                <CellWrapper hasIcon={true}>
                    <Icon type={item.zoneType || 'View'} size='small' />
                    {item.zone ? (
                        <CellContentWrapper content={`${item.zone} [${item.view}]`} />
                    ) : (
                        <CellContentWrapper content={item.view} />
                    )}
                </CellWrapper>
            );
        },
        comparator: (a, b) => stringCompare(a.zone, b.zone),
        style: { width: '50%' },
    },
    {
        id: 'transfer',
        header: 'Zone Transfer Interface',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.transfer} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.transfer, b.transfer),
        style: { width: '25%' },
    },
];
const DETAIL_ROLE_SERVER_GROUP_COLUMNS_WITH_INHERIT = [
    ...DETAIL_ROLE_SERVER_GROUP_COLUMNS,
    INHERIT_COLUMN,
];

const DETAIL_COLUMNS_OBJECT = {
    zone: DETAIL_ZONE_GROUP_COLUMNS,
    role: DETAIL_ROLE_GROUP_COLUMNS,
    server: DETAIL_SERVER_GROUP_COLUMNS,
    role_server: DETAIL_ROLE_SERVER_GROUP_COLUMNS,
};

const DETAIL_COLUMNS_OBJECT_INHERIT = {
    zone: DETAIL_ZONE_GROUP_COLUMNS_WITH_INHERIT,
    role: DETAIL_ROLE_GROUP_COLUMNS_WITH_INHERIT,
    server: DETAIL_SERVER_GROUP_COLUMNS_WITH_INHERIT,
    role_server: DETAIL_ROLE_SERVER_GROUP_COLUMNS_WITH_INHERIT,
};

const GROUP_ZONE_COLUMNS = [
    {
        id: 'zone',
        header: 'Zone',
        value: (item) => {
            return (
                <CellWrapper>
                    <Icon type={item.zoneType || 'View'} size='small' />
                    {item.zone ? (
                        <CellContentWrapper content={`${item.zone} [${item.view}]`} />
                    ) : (
                        <CellContentWrapper content={item.view} />
                    )}
                </CellWrapper>
            );
        },
        comparator: (a, b) => stringCompare(a.zone, b.zone),
        style: { width: '45%' },
    },
    {
        id: 'role',
        header: 'Roles',
        value: (item) => item.role,
        comparator: (a, b) => stringCompare(a.role, b.role),
        style: { width: '55%' },
    },
];

const GROUP_ROLE_COLUMNS = [
    {
        id: 'role',
        header: 'Role',
        value: (item) => item.role,
        comparator: (a, b) => stringCompare(a.role, b.role),
        style: { width: '180px' },
    },
    {
        id: 'views',
        header: 'Views',
        value: (item) => item.views,
        comparator: (a, b) => stringCompare(a.views, b.views),
    },
    {
        id: 'zones',
        header: 'Zones',
        value: (item) => item.zones,
        comparator: (a, b) => stringCompare(a.zones, b.zones),
    },
];

const GROUP_SERVER_COLUMNS = [
    {
        id: 'server',
        header: 'Server',
        value: (item) => item.server,
        comparator: (a, b) => stringCompare(a.server, b.server),
        style: { width: '20%' },
    },
    {
        id: 'views',
        header: 'Views',
        value: (item) => item.views,
        comparator: (a, b) => stringCompare(a.views, b.views),
        style: { width: '40%' },
    },
    {
        id: 'zones',
        header: 'Zones',
        value: (item) => item.zones,
        comparator: (a, b) => stringCompare(a.zones, b.zones),
        style: { width: '40%' },
    },
];

const GROUP_ROLE_SERVER_COLUMNS = [
    {
        id: 'server',
        header: 'Server',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.server} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.server, b.server),
        style: { width: '20%' },
    },
    {
        id: 'role',
        header: 'Role',
        value: (item) => item.role,
        comparator: (a, b) => stringCompare(a.role, b.role),
        style: { minWidth: '200px' },
    },
    {
        id: 'views',
        header: 'Views',
        value: (item) => item.views,
        comparator: (a, b) => stringCompare(a.views, b.views),
        style: { width: '40%' },
    },
    {
        id: 'zones',
        header: 'Zones',
        value: (item) => item.zones,
        comparator: (a, b) => stringCompare(a.zones, b.zones),
        style: { width: '40%' },
    },
];

const DEPLOYMENT_OPTION_COLUMNS = [
    {
        id: 'option',
        header: 'Option',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.option} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.option, b.option),
        style: { width: '32%' },
    },
    {
        id: 'server',
        header: 'Server',
        value: (item) => {
            return (
                <CellWrapper hasIcon={true}>
                    <Icon type={item.serverType} size='small' />
                    <CellContentWrapper content={item.server} />
                </CellWrapper>
            );
        },
        comparator: (a, b) => stringCompare(a.server, b.server),
        style: { width: '32%' },
    },
    {
        id: 'service_options',
        header: 'Service Option Values',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.service_options} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.service_options, b.service_options),
        style: { width: '32%' },
    },
];

const DEPLOYMENT_OPTION_COLUMNS_WITH_INHERIT = [
    ...DEPLOYMENT_OPTION_COLUMNS,
    {
        id: 'inherited',
        header: '	Inherited From',
        value: (item) => {
            return (
                <CellWrapper hasIcon={item.inheritedType}>
                    {item.inheritedType && <Icon type={item.inheritedType} size='small' />}
                    <CellContentWrapper content={item.inherited} />
                </CellWrapper>
            );
        },
        comparator: (a, b) => stringCompare(a.inherited, b.inherited),
        style: { width: '25%' },
    },
];

const DELETE_ACTION_CONFIRM_COLUMNS = [
    {
        id: 'zone',
        header: 'Zone',
        value: (item) => {
            return (
                <CellWrapper hasIcon={true}>
                    <Icon type={item.zoneType || 'View'} size='small' />
                    {item.zone ? (
                        <CellContentWrapper
                            content={`${item.zone} ${item.view ? ' [' + item.view + ']' : ''}`}
                        />
                    ) : (
                        <CellContentWrapper content={item.view} />
                    )}
                </CellWrapper>
            );
        },
        style: { width: '30%' },
    },
    {
        id: 'interface',
        header: 'Interface Name',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.interface} />
            </CellWrapper>
        ),
        style: { width: '30%' },
    },
    {
        id: 'role',
        header: 'Role',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.role} />
            </CellWrapper>
        ),
        style: { width: '20%' },
    },
    {
        id: 'status',
        header: 'Status',
        value: (item) => (
            <StatusIcon
                tooltipText={item.message}
                status={item.status === 'AVAILABLE' ? 'success' : 'fail'}
            />
        ),

        style: { maxWidth: '20%' },
    },
];

const ACTION_BEFORE_CHANGE_COLUMNS = [
    {
        id: 'zone',
        header: 'Zone',
        value: (item) => {
            return (
                <CellWrapper hasIcon={true}>
                    <Icon type={item.zoneType || 'View'} size='small' />
                    {item.zone ? (
                        <CellContentWrapper
                            content={`${item.zone} ${item.view ? ' [' + item.view + ']' : ''}`}
                        />
                    ) : (
                        <CellContentWrapper content={item.view} />
                    )}
                </CellWrapper>
            );
        },
        style: { width: '50%' },
    },
    {
        id: 'interface',
        header: 'Interface Name',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.interface} />
            </CellWrapper>
        ),
        style: { width: '25%' },
    },
    {
        id: 'role',
        header: 'Role',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.role} />
            </CellWrapper>
        ),
        style: { width: '25%' },
    },
];

const ACTION_AFTER_CHANGE_COLUMNS = [
    {
        id: 'zone',
        header: 'Zone',
        value: (item) => {
            return (
                <CellWrapper hasIcon={true}>
                    <Icon type={item.zoneType || 'View'} size='small' />
                    {item.zone ? (
                        <CellContentWrapper
                            content={`${item.zone} ${item.view ? ' [' + item.view + ']' : ''}`}
                        />
                    ) : (
                        <CellContentWrapper content={item.view} />
                    )}
                </CellWrapper>
            );
        },
        style: { width: '50%' },
    },
    {
        id: 'interface',
        header: 'Interface Name',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.interface} />
            </CellWrapper>
        ),
        style: { width: '25%' },
    },
    {
        id: 'role',
        header: 'Role',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.role} />
            </CellWrapper>
        ),
        style: { width: '25%' },
    },
    {
        id: 'status',
        header: 'Status',
        value: (item) => (
            <StatusIcon
                tooltipText={item.message}
                status={
                    item.status === 'AVAILABLE'
                        ? 'success'
                        : item.status === 'WARNING'
                        ? 'warning'
                        : item.status === 'INFO'
                        ? 'info'
                        : 'fail'
                }
            />
        ),

        style: { maxWidth: '72px' },
    },
];

const ACTION_RESULT_COLUMNS = [
    {
        id: 'type',
        header: 'Type',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.type} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.type, b.type),
        style: { width: '15%' },
    },
    {
        id: 'name',
        header: 'Name',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.absoluteName} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.absoluteName, b.absoluteName),
        style: { width: '35%' },
    },
    {
        id: 'roleType',
        header: 'Role Type',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.roleType} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.roleType, b.roleType),
        style: { width: '25%' },
    },
    {
        id: 'targetRoleType',
        header: 'Target Role Type',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.targetRoleType} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.targetRoleType, b.targetRoleType),
        style: { width: '25%' },
    },
    {
        id: 'status',
        header: 'Status',
        value: (item) => (
            <StatusIcon
                tooltipText={item.message}
                status={
                    item.status.includes('Successfully') || item.status.includes('SUCCESSFUL')
                        ? 'success'
                        : 'fail'
                }
            />
        ),
        comparator: (a, b) => stringCompare(a.status, b.status),
        style: { maxWidth: '72px' },
    },
];

const DELETE_RESULT_COLUMNS = [
    {
        id: 'type',
        header: 'Type',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.type} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.type, b.type),
        style: { width: '15%' },
    },
    {
        id: 'name',
        header: 'Name',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.absoluteName} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.absoluteName, b.absoluteName),
        style: { width: '35%' },
    },
    {
        id: 'roleType',
        header: 'Role Type',
        value: (item) => (
            <CellWrapper>
                <CellContentWrapper content={item.roleType} />
            </CellWrapper>
        ),
        comparator: (a, b) => stringCompare(a.roleType, b.roleType),
        style: { width: '25%' },
    },
    {
        id: 'status',
        header: 'Status',
        value: (item) => (
            <StatusIcon
                tooltipText={item.message}
                status={
                    item.status.includes('Successfully') || item.status.includes('SUCCESSFUL')
                        ? 'success'
                        : 'fail'
                }
            />
        ),
        comparator: (a, b) => stringCompare(a.status, b.status),
        style: { maxWidth: '25%' },
    },
];

const TABLE_CELL_TOOLTIP_ID = 'TABLE_CELL_TOOLTIP_ID';

export {
    DEFAULT_COLUMNS,
    DEFAULT_COLUMNS_WITH_INHERIT,
    DETAIL_NO_GROUP_COLUMNS,
    DETAIL_NO_GROUP_COLUMNS_WITH_INHERIT,
    DETAIL_COLUMNS_OBJECT,
    DETAIL_COLUMNS_OBJECT_INHERIT,
    GROUP_ZONE_COLUMNS,
    GROUP_ROLE_COLUMNS,
    GROUP_SERVER_COLUMNS,
    GROUP_ROLE_SERVER_COLUMNS,
    DEPLOYMENT_OPTION_COLUMNS,
    DEPLOYMENT_OPTION_COLUMNS_WITH_INHERIT,
    PAGE_SIZE,
    DELETE_ACTION_CONFIRM_COLUMNS,
    ACTION_BEFORE_CHANGE_COLUMNS,
    ACTION_AFTER_CHANGE_COLUMNS,
    ACTION_RESULT_COLUMNS,
    DELETE_RESULT_COLUMNS,
    TABLE_CELL_TOOLTIP_ID,
};
