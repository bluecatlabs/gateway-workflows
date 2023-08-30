import { FilterList, FilterMenu } from '@bluecateng/pelagos';
import React, { useMemo, useState } from 'react';
import { FILTER_LABELS, FILTER_MENU_OPTIONS, GROUP_ROLE_LABELS } from '../constants/filter';
import { compareObjects } from '../utils/common';
import { formatFilterItems } from '../utils/filter';
import TooltipToggleField from './fields/TooltipToggleField';
import './Filter.less';
import FilterForm from './FilterForm';
import Icon from './icons/Icon';

function Filter(props) {
    const { filter, onChangeFilter } = props;
    const [filterTemp, setFilterTemp] = useState(filter);
    const [roleOption, setRoleOption] = useState('group_role');

    const resetFilterTemp = () => {
        setFilterTemp({ ...filter });
        if (filter['custom_role'].length > 0) setRoleOption('custom_role');
        else setRoleOption('group_role');
    };

    const duplicateInterface = useMemo(
        () =>
            filterTemp.interfaceList
                .map((s) => s.serverInterface.name)
                .includes(filterTemp.svInterface?.name),
        [filterTemp.svInterface, filterTemp.interfaceList],
    );

    const handleApplyFilterList = (filterName, value) => {
        const key = filterName.includes('role') ? roleOption : filterName;
        const newFilter = { ...filter };
        const updated = { ...filterTemp };

        if (roleOption === 'group_role') newFilter['custom_role'] = [];
        else newFilter['group_role'] = [];

        if (updated.server.value && updated.svInterface) {
            if (!duplicateInterface && updated.svInterface.name !== 'Select Interface')
                updated.interfaceList = [
                    ...updated.interfaceList,
                    { server: updated.server, serverInterface: updated.svInterface },
                ];
            updated.server = {};
            updated.svInterface = null;
        }

        if (value) {
            onChangeFilter({
                ...newFilter,
                ...updated,
            });
            setFilterTemp({
                ...newFilter,
                ...updated,
            });
        } else {
            newFilter[key] = [];
            onChangeFilter(newFilter);
            setFilterTemp(newFilter);
        }
    };

    const handleApplyFilterMenu = (filterName, value) => {
        const key = filterName === 'role' ? roleOption : filterName;
        const newFilter = { ...filter };
        const updated = { ...filterTemp };

        if (roleOption === 'group_role') newFilter['custom_role'] = [];
        else newFilter['group_role'] = [];

        if (updated.server.value && updated.svInterface) {
            if (!duplicateInterface && updated.svInterface.name !== 'Select Interface')
                updated.interfaceList = [
                    ...updated.interfaceList,
                    { server: updated.server, serverInterface: updated.svInterface },
                ];
            updated.server = {};
            updated.svInterface = null;
        }

        setFilterTemp({
            ...newFilter,
            ...updated,
        });
        if (updated[key].length === 0 && filter[key].length === 0) return;
        onChangeFilter({
            ...newFilter,
            ...updated,
        });
    };

    const renderValueList = (items) => {
        const lastValue = items.slice(-1)[0].value;
        return items.map((item) => {
            return (
                <div className='filter-values'>
                    {typeof item.value === 'object' && <Icon type={item.value.type} size='small' />}
                    {(item.label || GROUP_ROLE_LABELS[item]) +
                        (compareObjects(lastValue, item.value) ? '' : ', ')}
                </div>
            );
        });
    };

    return (
        <>
            <FilterList
                className={'filter-list'}
                filters={formatFilterItems(filter)}
                onApply={handleApplyFilterList}
                getEditor={(name) => {
                    return (
                        <FilterForm
                            name={name}
                            title={'Edit Filter'}
                            filterTemp={filterTemp}
                            onChangeFilterTemp={(newFilter) => {
                                setFilterTemp(newFilter);
                            }}
                            resetFilterTemp={resetFilterTemp}
                            roleOption={roleOption}
                            onChangeRoleOption={(v) => setRoleOption(v)}
                        />
                    );
                }}
                getFilterTitle={(key) => FILTER_LABELS[key.includes('role') ? 'role' : key]}
                getValues={(key, v) => renderValueList(formatFilterItems(filter)[key])}
            />

            <FilterMenu
                flipped={true}
                getEditor={(name) => {
                    return (
                        <FilterForm
                            name={name}
                            title={'Edit Filter'}
                            filterTemp={filterTemp}
                            onChangeFilterTemp={(newFilter) => {
                                setFilterTemp(newFilter);
                            }}
                            resetFilterTemp={resetFilterTemp}
                            roleOption={roleOption}
                            onChangeRoleOption={(v) => setRoleOption(v)}
                        />
                    );
                }}
                getOptionText={(option) => FILTER_LABELS[option]}
                onApply={handleApplyFilterMenu}
                options={FILTER_MENU_OPTIONS}
            />
        </>
    );
}

export default Filter;
