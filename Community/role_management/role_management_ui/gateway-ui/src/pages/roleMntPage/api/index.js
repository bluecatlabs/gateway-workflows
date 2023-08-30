import { doGet, doPost } from '@bluecat/limani';
import { ACTION_NAME_TO_API_PARAM } from '../constants/action';
import { PAGE_SIZE } from '../constants/table';
import { formatFilterOption } from '../processors/common';
import { optionsToParamValue, roleOptionsToParamValue } from '../utils/api';

const BASE_URL = '/role-management/v1';

const getConfigurationsApi = () => {
    return doGet(`${BASE_URL}/configurations`);
};

const getRolesApi = ({ config, view, groupBy, containInherited, filter, pagination }) => {
    let url = `${BASE_URL}/configuration/${config}/view/${view}/dns_deployment_roles?`;

    let group = 'allRoles';
    switch (groupBy.value) {
        case 'zone':
            group = 'parentEntity';
            break;
        case 'role':
            group = 'roleType';
            break;
        case 'server':
            group = 'serverInterface';
            break;
        case 'role_server':
            group = 'roleServer';
    }
    url += `group_by=${group}`;

    let roleGroup = 'allRoles';
    if (filter.group_role.length > 0) roleGroup = filter.group_role[0];
    url += `&role_groups=${roleGroup}`;

    url += `&contain_inherited=${containInherited.value}`;

    if (filter.custom_role.length > 0) {
        url += `&custom_role_group=${roleOptionsToParamValue(filter.custom_role)}`;
    }
    if (filter.interfaceList.length > 0) {
        url += `&server_interface_names=${optionsToParamValue(
            filter.interfaceList.map((i) => ({ label: i.serverInterface.name })),
        )}`;
    }

    if (filter.zone.length > 0) {
        url += `&zone_names=${optionsToParamValue(filter.zone)}`;
    }
    if (filter.reverseZone.length > 0) {
        let networkReverseZone = [];
        let blockReverseZone = [];

        filter.reverseZone.map((item) => {
            if (item.value.type == 'Network') {
                networkReverseZone.push(item);
            } else {
                blockReverseZone.push(item);
            }
        });
        if (blockReverseZone.length > 0) {
            url += `&blocks=${optionsToParamValue(blockReverseZone)}`;
        }
        if (networkReverseZone.length > 0) {
            url += `&networks=${optionsToParamValue(networkReverseZone)}`;
        }
    }

    url += `&offset=${pagination.start}&limit=${PAGE_SIZE}`;

    return doGet(url);
};

const getDeploymentOptionApi = ({ collection, collectionName, view, config, server }) => {
    let url = `${BASE_URL}/configurations/${config}/deployment_options?collection=${collection}`;
    if (collectionName) url += `&collection_name=${collectionName}`;
    if (view) url += `&view=${view}`;
    if (server) url += `&server=${server}`;

    return doGet(url);
};

const getOptionsApi = ({ config, view, fieldName, prefix, selectedOptions }) => {
    if (!prefix) return [];

    const mapping = {
        serverInterface: 'interfaces',
        server: 'servers',
        zone: 'zones',
        view: 'views',
        reverseZone: 'reverse_zones',
    };

    let count = 0;
    if (selectedOptions) count += selectedOptions.length;

    let url = `${BASE_URL}/configurations/${config}/${mapping[fieldName]}`;
    if (prefix) url += `?hint=${prefix}&limit=${10 + count}`;
    if (view && fieldName === 'zone') url += prefix ? `&view_name=${view}` : `?view_name=${view}`;

    return new Promise((resolve, reject) => {
        if (prefix)
            doGet(url)
                .then((res) => {
                    let options = res.data.map((o) => formatFilterOption({ fieldName, option: o }));

                    if (selectedOptions) {
                        options = options.filter(
                            (o) =>
                                !selectedOptions
                                    .map((x) => JSON.stringify(x))
                                    .includes(JSON.stringify(o)),
                        );
                    }
                    resolve(options);
                })
                .catch((error) => {
                    console.log(error);
                    reject(error);
                });
    });
};

const getViewOptionsApi = ({ config }) => {
    let url = `${BASE_URL}/configurations/${config}/views`;

    return new Promise((resolve, reject) => {
        doGet(url)
            .then((res) => {
                const options = res.data.map((o) =>
                    formatFilterOption({ fieldName: 'views', option: o }),
                );
                resolve(options);
            })
            .catch((error) => {
                console.log(error);
                reject(error);
            });
    });
};

const doActionApi = ({ config, selectedAction, actionPayload, validate }) => {
    const url = `${BASE_URL}/configuration/${config}/deployment_roles?validate=${validate}&action=${
        ACTION_NAME_TO_API_PARAM[selectedAction.name]
    }`;

    return doPost(url, actionPayload, 'application/json');
};

const migrateApi = ({ config, selectedAction, actionPayload }) => {
    const url = `${BASE_URL}/configuration/${config}/deployment_roles/migration?action=${
        ACTION_NAME_TO_API_PARAM[selectedAction.name]
    }`;
    const headers = {
        Accept: 'application/json, */*;q=0.5',
        'Content-Type': 'application/json',
    };

    return fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(actionPayload),
    });
};

const getInterfacesByServerApi = ({ config, server }) => {
    const url = `${BASE_URL}/configurations/${config}/servers/${server}/interfaces`;
    return doGet(url);
};

const getServerByInterface = ({ config, hint }) => {
    const url = `${BASE_URL}/configurations/${config}/interfaces?hint=${hint}`;
    return doGet(url);
};

const getParentByType = (collections, object_id) => {
    const url = `${BASE_URL}/parent/${object_id}?collections=${collections}`;
    return doGet(url);
};

export {
    getRolesApi,
    getDeploymentOptionApi,
    getOptionsApi,
    getViewOptionsApi,
    getConfigurationsApi,
    doActionApi,
    migrateApi,
    getInterfacesByServerApi,
    getParentByType,
    getServerByInterface,
};
