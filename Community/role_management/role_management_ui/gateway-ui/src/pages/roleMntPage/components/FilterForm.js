import { RadioGroup, IconButton, LabelLine, timesThin } from '@bluecateng/pelagos';
import { faPlus } from '@fortawesome/free-solid-svg-icons';
import React, { useEffect, useMemo, useState, useContext, useCallback } from 'react';
import { getInterfacesByServerApi, getOptionsApi } from '../api';
import {
    FILTER_LABELS,
    GROUP_ROLE_LABELS,
    ROLE_OPTIONS,
    ROLE_OPTION_LABELS,
} from '../constants/filter';
import DropDownField from '../pelagos-components/DropDownField';
import MultipleAutocomplete from './fields/MultipleAutocomplete';
import ReloadMultipleAutocomplete from './fields/ReloadMultipleAutocomplete';
import ReloadAutocomplete from './fields/ReloadAutocomplete';
import './FilterForm.less';
import AppContext from '../AppContext';

function FilterForm(props) {
    const appContext = useContext(AppContext);
    const {
        name,
        title,
        filterTemp,
        onChangeFilterTemp,
        resetFilterTemp,
        roleOption,
        onChangeRoleOption,
    } = props;

    const key = useMemo(() => {
        if (name.includes('role')) {
            return roleOption;
        }
        return name;
    }, [roleOption]);

    useEffect(() => {
        resetFilterTemp();
    }, []);

    const [interfaceOptions, setInterfaceOptions] = useState([]);
    const [addInterfaceFlag, setAddInterfaceFlag] = useState(false);

    const getInterfaceOptions = async (server) => {
        if (!server.value) {
            setInterfaceOptions([]);
            onChangeFilterTemp({ ...filterTemp, svInterface: null });
            return;
        }

        const res = await getInterfacesByServerApi({
            config: appContext.config,
            server: server.value,
        });
        const options = res.data.map(({ name, managementAddress, primaryAddress }) => ({
            name,
            ip: managementAddress || primaryAddress,
        }));
        if (options.length > 1) options.unshift({ name: 'Select Interface', ip: null });

        setInterfaceOptions(options);
        onChangeFilterTemp({ ...filterTemp, svInterface: options[0] });
    };

    const duplicateInterface = (svInterface) => {
        return filterTemp.interfaceList
            .map((s) => s.serverInterface.name)
            .includes(svInterface.name);
    };

    const addServerInterface = () => {
        if (duplicateInterface(filterTemp.svInterface)) {
            return;
        }

        const interfaceData = [
            {
                server: filterTemp.server,
                serverInterface: filterTemp.svInterface,
            },
        ];

        onChangeFilterTemp({
            ...filterTemp,
            interfaceList: [...filterTemp.interfaceList, ...interfaceData],
            server: {},
            svInterface: null,
        });

        setInterfaceOptions([]);
        setAddInterfaceFlag(!addInterfaceFlag);
    };
    const removeServerInterface = useCallback(
        (event) => {
            const target = event.target.closest('button');
            if (target) {
                const index = +target.dataset.index;

                onChangeFilterTemp({
                    ...filterTemp,
                    interfaceList: filterTemp.interfaceList.filter((_, i) => i !== index),
                });
            }
        },

        [onChangeFilterTemp, filterTemp.interfaceList],
    );

    useEffect(() => {
        getInterfaceOptions(filterTemp.server);
    }, [filterTemp.server]);

    return (
        <div className='FilterForm'>
            <div style={{ display: 'inline' }}>
                <span>{title}</span>
            </div>

            {name === 'interfaceList' && (
                <>
                    <div className='serverInput'>
                        <ReloadAutocomplete
                            className={`serverInput__server`}
                            fieldName={'server'}
                            label={'Server'}
                            tag={filterTemp.server}
                            onChange={(newValue) => {
                                onChangeFilterTemp({ ...filterTemp, server: newValue });
                            }}
                            getOptions={getOptionsApi}
                            resetTextFlag={addInterfaceFlag}
                        />
                        <DropDownField
                            className='serverInput__interface'
                            label='Server Interface'
                            options={interfaceOptions}
                            renderOption={(v) => (v.ip ? `${v.name} [${v.ip}]` : v.name)}
                            value={filterTemp.svInterface}
                            onChange={(value) => {
                                onChangeFilterTemp({ ...filterTemp, svInterface: value });
                            }}
                            disabled={interfaceOptions.length < 2 || !filterTemp.server.value}
                        />

                        <IconButton
                            className='serverInput__addIcon'
                            icon={faPlus}
                            type='ghost'
                            size='medium'
                            disabled={
                                !filterTemp.server.value ||
                                !filterTemp.svInterface?.ip ||
                                duplicateInterface(filterTemp.svInterface)
                            }
                            onClick={addServerInterface}
                        />
                    </div>

                    <LabelLine
                        className='serverInterface_label'
                        text='Selected server interfaces'
                    />
                    <div
                        className='serverInterface__list'
                        role='list'
                        onClick={removeServerInterface}>
                        {filterTemp.interfaceList?.map((item, index) => {
                            const serverName = item.server.value;
                            const interfaceName = item.serverInterface.name;
                            return (
                                <div
                                    key={index}
                                    className='serverInterface__entry'
                                    tabIndex='0'
                                    role='listitem'
                                    data-index={index}>
                                    <IconButton
                                        className='serverInterface__icon'
                                        icon={timesThin}
                                        data-index={index}
                                    />

                                    {`${serverName} [${interfaceName}]`}
                                </div>
                            );
                        })}
                    </div>
                </>
            )}

            {name.includes('role') && (
                <>
                    <RadioGroup
                        id='normal'
                        options={['group_role', 'custom_role']}
                        className='roleGroup-radio'
                        renderLabel={(option) => ROLE_OPTION_LABELS[option]}
                        value={roleOption}
                        onChange={onChangeRoleOption}
                    />

                    {key === 'group_role' ? (
                        <DropDownField
                            label={FILTER_LABELS[key]}
                            options={Object.keys(GROUP_ROLE_LABELS)}
                            renderOption={(k) => GROUP_ROLE_LABELS[k]}
                            value={filterTemp[key][0] || 'allRoles'}
                            onChange={(newValue) =>
                                onChangeFilterTemp({
                                    ...filterTemp,
                                    [key]: newValue !== 'allRoles' ? [newValue] : [],
                                })
                            }
                        />
                    ) : (
                        <MultipleAutocomplete
                            label={FILTER_LABELS[key]}
                            options={ROLE_OPTIONS}
                            tags={filterTemp[key]}
                            onChange={(newList) =>
                                onChangeFilterTemp({
                                    ...filterTemp,
                                    [key]: newList,
                                })
                            }
                        />
                    )}
                </>
            )}

            {!name.includes('role') && name !== 'interfaceList' && (
                <ReloadMultipleAutocomplete
                    fieldName={key}
                    filterField={true}
                    label={FILTER_LABELS[key]}
                    tags={filterTemp[key]}
                    onChange={(newList) =>
                        onChangeFilterTemp({
                            ...filterTemp,
                            [key]: newList,
                        })
                    }
                    getOptions={getOptionsApi}
                />
            )}
        </div>
    );
}

export default FilterForm;
