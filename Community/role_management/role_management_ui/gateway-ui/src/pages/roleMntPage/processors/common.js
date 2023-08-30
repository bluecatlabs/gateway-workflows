import { ACTION_NAMES } from '../constants/action';
import { getSelectedDeployment, getSelectedRoles } from './table';

// prepare data for calling api
export const getDeploymentOptionParam = ({ config, role, fromDeploymentOptionData, server }) => {
    if (fromDeploymentOptionData)
        return {
            collection: role.collection,
            collectionName: role.collectionName,
            view: role.collection === 'blocks' || role.collection === 'networks' ? null : role.view,
            config,
            server,
        };

    let view = role.view.name;
    let collection = 'views';
    let collectionName = role.view.name;

    if (role.zone) {
        collection = 'zones';
        collectionName = role.zone.absoluteName;
    } else if (role.block) {
        collection = 'blocks';
        collectionName = role.block.range;
        view = null;
    } else if (role.network) {
        collection = 'networks';
        collectionName = role.network.range;
        view = null;
    }

    return {
        collection,
        collectionName,
        view,
        config,
        server,
    };
};

const getCollectionType = (role) => {
    let collection = 'views';
    if (role.zone) {
        collection = 'zones';
    } else if (role.block) {
        collection = 'blocks';
    } else if (role.network) {
        collection = 'networks';
    }
    return collection;
};

const convertRoleToPayloadItem = (role) => {
    const collectionType = getCollectionType(role);
    const result = {
        collection: collectionType,
        role_type: role.roleType,
        server_interface: role.serverInterface?.name,
    };
    switch (collectionType) {
        case 'views':
            result.name = role.view.name;
            break;
        case 'zones':
            result.view = role.view.name;
            result.absolute_name = role.zone.absoluteName;
            break;
        case 'blocks':
            result.range = role.block.range;
            break;
        case 'networks':
            result.range = role.network.range;
            break;
    }
    return result;
};

export const getActionPayload = ({
    selectedAction,
    groupBy,
    roles,
    selected,
    destination,
    view,
    deploymentData,
    optionSelected,
}) => {
    let payload = {};
    let selectedRoles = getSelectedRoles(roles, groupBy, selected);
    let role = [];
    let targetRoles = [];
    let options = [];
    let optionFull = getSelectedDeployment(deploymentData, optionSelected);

    optionFull?.map((item) => {
        options.push({ name: item.name, value: item.value });
    });

    switch (selectedAction.name) {
        case ACTION_NAMES.HIDE_ROLES:
        case ACTION_NAMES.EXPOSE_ROLES:
        case ACTION_NAMES.DELETE_ROLES:
            payload = { roles: selectedRoles.map((role) => convertRoleToPayloadItem(role)) };
            break;

        case ACTION_NAMES.COPY_ROLES_TO_ZONES:
            const mergeZonesWithSameView = (list, mergeField) => {
                const sortedList = list.sort((a, b) => {
                    return a.view > b.view ? 1 : -1;
                });
                const views = [];
                const result = [];
                for (const item of sortedList) {
                    if (!views.includes(item.view)) {
                        views.push(item.view);
                        result.push(item);
                    } else {
                        result[result.length - 1][mergeField].push(item[mergeField][0]);
                    }
                }

                return result;
            };
            if (destination.zoneList.length > 0) {
                targetRoles.push({
                    'collection': 'zones',
                    'absolute_names': destination.zoneList.map((z) => z.value.absoluteName),
                    'view': view,
                });
            }

            let reverseTargetRoles = [];
            if (destination.reverseZoneList.length > 0) {
                const reverseZones = destination.reverseZoneList.map((rZone) => ({
                    'collection': rZone.value.type === 'Block' ? 'blocks' : 'networks',
                    'ranges': [rZone.value.range],
                    'view': view,
                }));

                const blockZones = reverseZones.filter((z) => z.collection === 'blocks');
                const networkZones = reverseZones.filter((z) => z.collection === 'networks');

                reverseTargetRoles = mergeZonesWithSameView(blockZones, 'ranges').concat(
                    mergeZonesWithSameView(networkZones, 'ranges'),
                );
            }

            payload = {
                roles: selectedRoles.map((role) => convertRoleToPayloadItem(role)),
                target_roles: targetRoles.concat(reverseTargetRoles),
                options: options,
            };
            break;

        case ACTION_NAMES.COPY_ROLES_TO_SERVER:
            payload = {
                target_roles: [
                    {
                        server_interfaces: [destination.serverInterface.interface.name],
                        collection: 'interfaces',
                    },
                ],
                roles: selectedRoles.map((role) => convertRoleToPayloadItem(role)),
            };
            break;
        case ACTION_NAMES.MOVE_ROLES_TO_SERVER:
            payload = {
                target_roles: [
                    {
                        server_interfaces: [destination.serverInterface.interface.name],
                        collection: 'interfaces',
                    },
                ],
                roles: selectedRoles.map((role) => convertRoleToPayloadItem(role)),
            };
            break;
        case ACTION_NAMES.ADD_SERVERS:
            role.push(selectedRoles.map((role) => convertRoleToPayloadItem(role))[0]);
            payload = {
                target_roles: [
                    {
                        server_interfaces: destination.serverInterfaceList.map(
                            (item) => item.serverInterface.name,
                        ),
                        collection: 'interfaces',
                        view,
                        role_type: destination.roleType.value,
                        zone_transfer_interface: destination.zoneTransferInterface.interface.name,
                    },
                ],
                roles: role,
            };
            break;

        case ACTION_NAMES.MOVE_PRIMARY_ROLE:
            role.push(selectedRoles.map((role) => convertRoleToPayloadItem(role))[0]);
            payload = {
                target_roles: [
                    {
                        server_interfaces: [destination.serverInterface.interface.name],
                        collection: 'interfaces',
                    },
                ],
                roles: role,
            };
            break;
    }
    return payload;
};

// format data from api
export const formatFilterOption = ({ fieldName, option }) => {
    let value = option.name;
    let label = option.name;
    let id = option.id;

    switch (fieldName) {
        case 'zone':
            value = {
                absoluteName: option.absoluteName,
                viewName: option.view,
                forwarderZone: true,
            };
            label = option.absoluteName;
            id = null;
            break;
        case 'reverseZone':
            value = {
                range: option.range,
                type: option.type.includes('Block')
                    ? 'Block'
                    : option.type.includes('Network')
                    ? 'Network'
                    : '',
            };
            label = option.reverseZoneName;
            id = null;
            break;
    }

    return { value, label, id };
};
