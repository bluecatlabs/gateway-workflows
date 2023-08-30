import { GROUP_TO_COLUMNS } from '../constants/group';
import {
    DEFAULT_COLUMNS,
    DEFAULT_COLUMNS_WITH_INHERIT,
    DETAIL_COLUMNS_OBJECT,
    DETAIL_COLUMNS_OBJECT_INHERIT,
    DETAIL_NO_GROUP_COLUMNS,
    DETAIL_NO_GROUP_COLUMNS_WITH_INHERIT,
} from '../constants/table';

const setElementBackgroundColor = (id, color) => {
    const el = document.getElementById(id);
    if (el) el.style.backgroundColor = color;
};

const compareObjects = (o1, o2) => {
    return JSON.stringify(o1) === JSON.stringify(o2);
};

const listIncludesObj = (li, o) => {
    return li.map((e) => JSON.stringify(e)).includes(JSON.stringify(o));
};

const getSelectedKeys = (selected) => {
    if (!selected) return [];

    let result = [];
    for (const k of Object.keys(selected)) {
        if (selected[k]) result.push(k);
    }
    return result;
};

const getSelectedServerRoleMap = (selected) => {
    const jsonSelected = selected.map((x) => JSON.parse(x));
    let result = {};
    for (const o of jsonSelected) {
        if (!Object.keys(result).includes(o.server)) result[o.server] = [o.role];
        else result[o.server].push(o.role);
    }
    return result;
};

// For inherit roles, there are many roles with the same id, this func is to make the ids different
const preprocessData = (roles, groupBy, containInherited) => {
    if (!containInherited.value) return roles;

    let result = roles;
    if (!groupBy.value) {
        result = roles.map((role) => ({
            ...role,
            id: role.id.toString() + role?.zone?.name + (Math.random() * 999999).toString(),
        }));
    } else if (groupBy.value === 'zone' || groupBy.value === 'role' || groupBy.value === 'server') {
        result = roles.map((o) => ({
            ...o,
            roles: o.roles.map((x) => ({
                ...x,
                id: x.id.toString() + x?.zone?.name + (Math.random() * 999999).toString(),
            })),
        }));
    } else if (groupBy.value === 'role_server') {
        result = roles.map((o) => ({
            ...o,
            roles: o.roles.map((x) => ({
                ...x,
                roles: x.roles.map((y) => ({
                    ...y,
                    id: y.id.toString() + y?.zone?.name + (Math.random() * 999999).toString(),
                })),
            })),
        }));
    }

    return result;
};

const getDetailTableColumns = (groupBy, containInherited) => {
    if (groupBy.value) {
        if (containInherited) {
            return DETAIL_COLUMNS_OBJECT_INHERIT[groupBy.value];
        } else {
            return DETAIL_COLUMNS_OBJECT[groupBy.value];
        }
    } else {
        if (containInherited) {
            return DETAIL_NO_GROUP_COLUMNS_WITH_INHERIT;
        } else {
            return DETAIL_NO_GROUP_COLUMNS;
        }
    }
};

const getTableColumns = (groupBy, containInherited) => {
    if (!groupBy.value) {
        if (containInherited.value) {
            return DEFAULT_COLUMNS_WITH_INHERIT;
        }
        return DEFAULT_COLUMNS;
    } else {
        return GROUP_TO_COLUMNS[groupBy.value];
    }
};

export {
    setElementBackgroundColor,
    compareObjects,
    listIncludesObj,
    getSelectedKeys,
    getSelectedServerRoleMap,
    preprocessData,
    getDetailTableColumns,
    getTableColumns,
};
