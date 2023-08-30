import { getSelectedServerRoleMap } from '../utils/common';
import { ROLE_TYPE_LABELS } from '../constants/action';
import { getParentByType } from '../api';

const getZoneType = (data) => {
    let zoneType = '';
    if (data.zone?.absoluteName) zoneType = 'Zone';
    else if (data?.network?.reverseZoneName) zoneType = 'Network';
    else if (data?.block?.reverseZoneName) zoneType = 'Block';
    return zoneType;
};
const formatRole = (data) => {
    const zone =
        data.zone?.absoluteName || data?.network?.reverseZoneName || data?.block?.reverseZoneName;
    return {
        id: data.id,
        view: data.view?.name,
        zone,
        zoneType: getZoneType(data),
        server: data.serverInterface?.name,
        serverInterfaceId: data.serverInterface?.id,
        role: data.name,
        transfer: data.zoneTransferServerInterface?.name,
        inheritedFrom: data?._inheritedFrom || null,
    };
};

const parentIsView = (role) =>
    role?.zone?.type !== 'Zone' && !role?.network?.reverseZoneName && !role?.block?.id;
const getZone = (role) =>
    role.zone?.absoluteName || role.network?.reverseZoneName || role.block.reverseZoneName;
const genZoneGroupId = (roleGroup) => {
    const idObject = {
        id: roleGroup.parentEntity.id,
        type: roleGroup.parentEntity.type,
        name: roleGroup.parentEntity.absoluteName || roleGroup.parentEntity.reverseZoneName,
        viewName: Array.isArray(roleGroup.roles) ? roleGroup.roles[0].view.name : '',
    };
    return JSON.stringify(idObject);
};
const genServerRoleGroupId = ({ serverGroup, roleGroup }) => {
    const idObject = {
        server: serverGroup.serverInterface.name,
        role: roleGroup.roleType,
    };
    return JSON.stringify(idObject);
};

const formatRoleList = (roleList, groupBy) => {
    if (!groupBy.value) {
        return roleList.map((role) => formatRole(role));
    } else {
        try {
            let result = [];
            switch (groupBy.value) {
                case 'zone':
                    for (const group of roleList) {
                        result.push({
                            id: genZoneGroupId(group),
                            view: group.roles[0].view.name,
                            zone:
                                group.parentEntity.type === 'Zone'
                                    ? group.parentEntity.absoluteName
                                    : group.parentEntity.reverseZoneName,
                            zoneType: group.parentEntity.type.includes('Block')
                                ? 'Block'
                                : group.parentEntity.type.includes('Network')
                                ? 'Network'
                                : group.parentEntity.type === 'Zone'
                                ? 'Zone'
                                : '',
                            role: group.roles
                                .reduce((prev, current) => {
                                    return (
                                        prev + current.serverInterface.name + ` (${current.name}), `
                                    );
                                }, '')
                                .slice(0, -2),
                        });
                    }
                    return result;

                case 'role':
                    for (const group of roleList) {
                        result.push({
                            id: group.roleType,
                            role: group.roles[0].name,
                            zones: group.roles
                                .filter((role) => !parentIsView(role))
                                .reduce((prev, current) => {
                                    return (
                                        prev +
                                        getZone(current) +
                                        ` (${current.serverInterface.name}), `
                                    );
                                }, '')
                                .slice(0, -2),
                            views: group.roles
                                .filter((role) => parentIsView(role))
                                .reduce((prev, current) => {
                                    return (
                                        prev +
                                        current.view.name +
                                        ` (${current.serverInterface.name}), `
                                    );
                                }, '')
                                .slice(0, -2),
                        });
                    }
                    return result;
                case 'server':
                    for (const group of roleList) {
                        result.push({
                            id: group.serverInterface.name,
                            server: group.serverInterface.name,
                            serverInterfaceId: group.serverInterface.id,
                            zones: group.roles
                                .filter((role) => !parentIsView(role))
                                .reduce((prev, current) => {
                                    return prev + getZone(current) + ` (${current.name}), `;
                                }, '')
                                .slice(0, -2),
                            views: group.roles
                                .filter((role) => parentIsView(role))
                                .reduce((prev, current) => {
                                    return prev + current.view.name + ` (${current.name}), `;
                                }, '')
                                .slice(0, -2),
                        });
                    }
                    return result;
                case 'role_server':
                    for (const serverGroup of roleList) {
                        for (const roleGroup of serverGroup.roles) {
                            result.push({
                                id: genServerRoleGroupId({ serverGroup, roleGroup }),
                                server: serverGroup.serverInterface.name,
                                serverInterfaceId: serverGroup.serverInterface.id,
                                role: roleGroup.roles[0].name,
                                zones: roleGroup.roles
                                    .filter((role) => !parentIsView(role))
                                    .reduce((prev, current) => {
                                        return prev + getZone(current) + `, `;
                                    }, '')
                                    .slice(0, -2),
                                views: roleGroup.roles
                                    .filter((role) => parentIsView(role))
                                    .reduce((prev, current) => {
                                        return prev + current.view.name + `, `;
                                    }, '')
                                    .slice(0, -2),
                            });
                        }
                    }
                    return result;
            }
        } catch {
            // Handle case: lazy loading does not finish. but filter or group is applied
            return [];
        }
    }
};

const formatValidationData = ({ items, target }) => {
    const collectionToZoneType = {
        zones: 'Zone',
        blocks: 'Block',
        networks: 'Network',
    };

    return items.map((item) => {
        const result = {
            id: item.id,
            view: item.view || item.name,
            zone: item.absolute_name || item.reverse_zone,
            zoneType: collectionToZoneType[item.collection],
            interface: item.server_interface,
            role: ROLE_TYPE_LABELS[item.role_type],

            collection: item?.collection,
            collectionName:
                item.collection === 'views'
                    ? item.name
                    : item.collection === 'zones'
                    ? item.absolute_name
                    : item.range,
        };
        if (target === 'new_role') {
            result['status'] = item.status;
            result['message'] = item.message;
        }
        return result;
    });
};

const formatDataDeleteConfirm = (items) => {
    const checkZoneType = (item) => {
        let result;
        if (item.zone) {
            result = 'Zone';
        } else if (item.network) {
            result = 'Network';
        } else if (item.block) {
            result = 'Block';
        } else result = 'View';
        return result;
    };

    return items.map((item) => {
        const result = {
            id: item.id,
            zone:
                item?.zone?.absoluteName ||
                item?.network?.reverseZoneName ||
                item?.block?.reverseZoneName ||
                item?.view?.name,
            view: item?.view?.name,
            zoneType: checkZoneType(item),
            interface: item.serverInterface.name,
            role: ROLE_TYPE_LABELS[item.roleType],
        };

        return result;
    });
};

const getIds = (roleList, groupBy) => {
    if (!groupBy.value) {
        return roleList.map((role) => role.id);
    } else {
        switch (groupBy.value) {
            case 'zone':
                return roleList.map((group) => genZoneGroupId(group));

            case 'role':
                return roleList.map((group) => group.roleType);
            case 'server':
                return roleList.map((group) => group.serverInterface.name);
            case 'role_server':
                let result = [];
                for (const serverGroup of roleList) {
                    for (const roleGroup of serverGroup.roles) {
                        result.push(genServerRoleGroupId({ serverGroup, roleGroup }));
                    }
                }
                return result;
        }
    }
};

const getIdsDeployment = (list) => {
    return list?.map((item) => item.id);
};

const getSelectedRoles = (roleList, groupBy, selected) => {
    let selectedGroup;
    let roles;
    switch (groupBy.value) {
        case 'zone':
            selectedGroup = roleList.filter((roleGroup) =>
                selected.includes(genZoneGroupId(roleGroup)),
            );
            roles = selectedGroup.reduce(
                (result, currentGroup) => [...result, ...currentGroup.roles],
                [],
            );

            return roles;
        case 'server':
            selectedGroup = roleList.filter((roleGroup) =>
                selected.includes(roleGroup.serverInterface.name),
            );
            roles = selectedGroup.reduce(
                (result, currentGroup) => [
                    ...result,
                    ...currentGroup.roles.map((r) => ({
                        ...r,
                        serverInterface: currentGroup.serverInterface,
                    })),
                ],
                [],
            );

            return roles;
        case 'role':
            selectedGroup = roleList.filter((roleGroup) => selected.includes(roleGroup.roleType));
            roles = selectedGroup.reduce(
                (result, currentGroup) => [...result, ...currentGroup.roles],
                [],
            );
            roles = roles.map((role) => ({
                ...role,
                roleType: role.name.replace(' ', '_').toUpperCase(),
            }));

            return roles;
        case 'role_server':
            const selectedServerRole = getSelectedServerRoleMap(selected);
            selectedGroup = roleList
                .filter((roleGroup) =>
                    Object.keys(selectedServerRole).includes(roleGroup.serverInterface.name),
                )
                .map((o) => {
                    return {
                        roles: o.roles.filter((role) =>
                            selectedServerRole[o.serverInterface.name].includes(role.roleType),
                        ),
                        serverInterface: o.serverInterface,
                    };
                });

            roles = selectedGroup.reduce(
                (result, currentGroup) => [
                    ...result,
                    ...currentGroup.roles.reduce(
                        (r, c) => [
                            ...r,
                            ...c.roles.map((r) => ({
                                ...r,
                                serverInterface: currentGroup.serverInterface,
                            })),
                        ],
                        [],
                    ),
                ],
                [],
            );

            roles = roles.map((role) => ({
                ...role,
                roleType:
                    role.name == 'Forwarder'
                        ? 'FORWARDING'
                        : role.name.replace(' ', '_').toUpperCase(),
            }));

            return roles;
        default:
            roles = roleList.filter((role) => selected.includes(role.id.toString()));
            return roles;
    }
};

const getSelectedDeployment = (dnsList, selected) => {
    return dnsList?.filter((option) => selected.includes(option.id.toString()));
};

const getDetailData = (roleList, groupBy, item) => {
    switch (groupBy.value) {
        case 'zone':
            return roleList.filter((roleGroup) => genZoneGroupId(roleGroup) === item.id)[0].roles;

        case 'role':
            return roleList.filter((roleGroup) => roleGroup.roleType === item.id)[0].roles;

        case 'server':
            const { roles: serverRoles1, serverInterface: serverInterface1 } = roleList.filter(
                (roleGroup) => roleGroup.serverInterface.name === item.id,
            )[0];
            return serverRoles1.map((x) => ({ ...x, serverInterface: serverInterface1 }));

        case 'role_server':
            const jsonItem = JSON.parse(item.id);
            const server = jsonItem.server;
            const roleType = jsonItem.role.toUpperCase();

            const { roles: serverRoles2, serverInterface: serverInterface2 } = roleList.filter(
                (roleGroup) => roleGroup.serverInterface.name === server,
            )[0];

            return serverRoles2
                .filter((roleGroup) => roleGroup.roleType === roleType)[0]
                .roles.map((x) => ({ ...x, serverInterface: serverInterface2 }));

        default:
            return roleList.filter((role) => role.id === item.id);
    }
};

const formatDeploymentOption = (data) => {
    return {
        id: data.id,
        option: data.displayName,
        server: data?.serverScope?.name,
        serverType: data?.serverScope?.type,
        service_options: Array.isArray(data.value) ? data?.value?.join(', ') : data?.value,
        inherited: data._inheritedFrom ? data._inheritedFrom.name : '',
        inheritedType: data._inheritedFrom ? data._inheritedFrom.type : '',
    };
};

const formatActionResult = (data) => {
    const statusObj = Array.isArray(data.status) ? data.status[0] : data.status;
    return {
        id: data.type + data.name,
        type: data.type,
        name: data.name || data.range,
        absoluteName: data.absoluteName,
        roleType: statusObj ? ROLE_TYPE_LABELS[statusObj.roleType] : '',
        targetRoleType: statusObj ? ROLE_TYPE_LABELS[statusObj.targetRoleType] : '',
        status: statusObj ? statusObj.status : 'SUCCESSFUL', //????????????????????????????
        message: statusObj ? statusObj.message : '',
    };
};

export {
    formatRole,
    formatRoleList,
    formatValidationData,
    getIds,
    getDetailData,
    getSelectedRoles,
    formatDeploymentOption,
    formatActionResult,
    formatDataDeleteConfirm,
    getIdsDeployment,
    getSelectedDeployment,
};
