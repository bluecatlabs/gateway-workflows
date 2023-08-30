import { IconButton, LabelLine, timesThin } from '@bluecateng/pelagos';
import { faPlus } from '@fortawesome/free-solid-svg-icons';
import React, { useCallback, useContext, useEffect, useState } from 'react';
import { getInterfacesByServerApi, getOptionsApi } from '../api';
import AppContext from '../AppContext';
import { ACTION_NAMES, ADD_SERVERS_ROLE_TYPE_OPTIONS } from '../constants/action';
import DropDownField from '../pelagos-components/DropDownField';
import './DestinationForm.less';
import ReloadAutocomplete from './fields/ReloadAutocomplete';
import ReloadMultipleAutocomplete from './fields/ReloadMultipleAutocomplete';

function DestinationForm(props) {
    const appContext = useContext(AppContext);
    const { selectedActionName, destination, onChange, onChangeMultiple } = props;

    const [addInterfaceFlag, setAddInterfaceFlag] = useState(false);

    const [interfaceOptions, setInterfaceOptions] = useState({ main: [], transfer: [] });
    const [interfaceError, setInterfaceError] = useState({ main: '', transfer: '' });

    const removeServerInterface = useCallback(
        (event) => {
            const target = event.target.closest('button');
            if (target) {
                const index = +target.dataset.index;
                onChange(
                    'serverInterfaceList',
                    destination.serverInterfaceList.filter((_, i) => i !== index),
                );
            }
        },
        [onChange, destination.serverInterfaceList],
    );

    const duplicateInterface = (svInterface) => {
        return destination.serverInterfaceList
            .map((s) => s.serverInterface.name)
            .includes(svInterface?.name);
    };

    const addServerInterface = () => {
        if (duplicateInterface(destination.candidateSvInterface)) {
            setInterfaceError({ ...interfaceError, main: 'Duplicate Item' });
            return;
        }

        const interfaceData = [
            {
                server: destination.candidateServer,
                serverInterface: destination.candidateSvInterface,
            },
        ];

        onChangeMultiple({
            serverInterfaceList: destination.serverInterfaceList.concat(interfaceData),
            candidateServer: {},
        });
        setAddInterfaceFlag(!addInterfaceFlag);
    };

    const updateSingleServerInterface = ({ type, value }) => {
        onChange('serverInterface', {
            ...destination['serverInterface'],
            [type]: value,
        });
    };

    const updateTransferInterface = ({ type, value }) => {
        onChange('zoneTransferInterface', {
            ...destination.zoneTransferInterface,
            [type]: value,
        });

        if (type === 'server') {
            setInterfaceError({ ...interfaceError, transfer: '' });
            return;
        }

        if (duplicateInterface(value)) {
            setInterfaceError({
                ...interfaceError,
                transfer: `Main and Zone Transfers Servers can't be the same server`,
            });
        } else setInterfaceError({ ...interfaceError, transfer: '' });
    };

    const getInterfaceOptions = async ({ type, singleInterface }) => {
        if (
            !destination.candidateServer.value &&
            !destination.zoneTransferInterface.server.value &&
            !destination.serverInterface.server.value
        ) {
            setInterfaceOptions({ ...interfaceOptions, [type]: [] });
            return;
        }

        const serverName =
            type === 'transfer'
                ? destination.zoneTransferInterface.server.value
                : singleInterface
                ? destination.serverInterface.server.value
                : destination.candidateServer?.value;

        if (!serverName) return;

        const res = await getInterfacesByServerApi({
            config: appContext.config,
            server: serverName,
        });
        const options = res.data.map(({ name, managementAddress, primaryAddress }) => ({
            name,
            ip: managementAddress || primaryAddress,
        }));
        if (options.length > 1) options.unshift({ name: 'Select Interface', ip: null });

        setInterfaceOptions({ ...interfaceOptions, [type]: options });
        const keepSelectedInterface = ({ options, svInterface }) => {
            const idx = options.map((o) => o.name).indexOf(svInterface?.name);
            return idx > 0 ? options[idx] : options[0];
        };

        if (type === 'transfer') {
            if (duplicateInterface(options[0])) {
                setInterfaceError({
                    ...interfaceError,
                    transfer: `Main and Zone Transfers Servers can't be the same server`,
                });
            } else setInterfaceError({ ...interfaceError, transfer: '' });

            onChange('zoneTransferInterface', {
                ...destination.zoneTransferInterface,
                interface: keepSelectedInterface({
                    options,
                    svInterface: destination.zoneTransferInterface.interface,
                }),
            });
        } else if (type === 'main') {
            if (singleInterface)
                onChange('serverInterface', {
                    ...destination.serverInterface,
                    interface: keepSelectedInterface({
                        options,
                        svInterface: destination.serverInterface.interface,
                    }),
                });
            else onChange('candidateSvInterface', options[0]);
        }
    };

    useEffect(() => {
        getInterfaceOptions({ type: 'main' });
    }, [destination.candidateServer]);

    useEffect(() => {
        getInterfaceOptions({ type: 'transfer' });
    }, [destination.zoneTransferInterface.server]);

    useEffect(() => {
        getInterfaceOptions({ type: 'main', singleInterface: true });
    }, [destination.serverInterface.server]);

    useEffect(() => {
        if (
            destination.zoneTransferInterface.server.value &&
            destination.zoneTransferInterface.interface.name
        ) {
            if (duplicateInterface(destination.zoneTransferInterface.interface)) {
                setInterfaceError({
                    ...interfaceError,
                    transfer: `Main and Zone Transfers Servers can't be the same server`,
                });
            } else setInterfaceError({ ...interfaceError, transfer: '' });
        }
    }, [destination.serverInterfaceList]);

    switch (selectedActionName) {
        case ACTION_NAMES.COPY_ROLES_TO_SERVER:
        case ACTION_NAMES.MOVE_ROLES_TO_SERVER:
        case ACTION_NAMES.MOVE_PRIMARY_ROLE:
            return (
                <div className='oneServerInput'>
                    <ReloadAutocomplete
                        className={`oneServerInput__server`}
                        fieldName={'server'}
                        label={'Server'}
                        tag={destination.serverInterface.server}
                        onChange={(o) => updateSingleServerInterface({ type: 'server', value: o })}
                        getOptions={getOptionsApi}
                    />

                    <DropDownField
                        className='oneServerInput__interface'
                        label='Server Interface'
                        value={destination.serverInterface.interface}
                        options={interfaceOptions.main}
                        renderOption={(v) => (v.ip ? `${v.name} [${v.ip}]` : v.name)}
                        disabled={
                            interfaceOptions.main.length < 2 || !destination.serverInterface.server
                        }
                        onChange={(v) =>
                            updateSingleServerInterface({ type: 'interface', value: v })
                        }
                    />
                </div>
            );
        case ACTION_NAMES.ADD_SERVERS:
            return (
                <div>
                    <div className='serverInput'>
                        <ReloadAutocomplete
                            className={`serverInput__server`}
                            fieldName={'server'}
                            label={'Server'}
                            tag={destination.candidateServer}
                            onChange={(newValue) => {
                                onChange('candidateServer', newValue);
                                setInterfaceError({ ...interfaceError, main: '' });
                            }}
                            getOptions={getOptionsApi}
                            resetTextFlag={addInterfaceFlag}
                        />
                        <DropDownField
                            className='serverInput__interface'
                            label='Server Interface'
                            value={destination.candidateSvInterface}
                            options={interfaceOptions.main}
                            renderOption={(v) => (v.ip ? `${v.name} [${v.ip}]` : v.name)}
                            disabled={
                                interfaceOptions.main.length < 2 || !destination.candidateServer
                            }
                            onChange={(value) => {
                                onChange('candidateSvInterface', value);
                                setInterfaceError({ ...interfaceError, main: '' });
                            }}
                            error={interfaceError.main}
                        />

                        <IconButton
                            className='serverInput__addIcon'
                            icon={faPlus}
                            type='ghost'
                            size='medium'
                            disabled={
                                !destination.candidateServer.value ||
                                !destination.candidateSvInterface ||
                                destination.candidateSvInterface.name === 'Select Interface'
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
                        {destination['serverInterfaceList']?.map((item, index) => {
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

                    <DropDownField
                        className='roleType'
                        label='Role Type'
                        value={destination['roleType']}
                        options={ADD_SERVERS_ROLE_TYPE_OPTIONS}
                        renderOption={(o) => o.label}
                        onChange={(newOption) => {
                            onChange('roleType', newOption);
                        }}
                    />

                    <div className='transferInterfaceInput'>
                        <ReloadAutocomplete
                            className={`transferInterfaceInput__server`}
                            fieldName={'server'}
                            label={'Zone Transfer Server'}
                            tag={destination.zoneTransferInterface.server}
                            onChange={(value) => updateTransferInterface({ type: 'server', value })}
                            getOptions={getOptionsApi}
                        />
                        <DropDownField
                            className='transferInterfaceInput__interface'
                            label='Zone Transfer Interface'
                            value={destination.zoneTransferInterface.interface}
                            options={interfaceOptions.transfer}
                            renderOption={(v) => (v.ip ? `${v.name} [${v.ip}]` : v.name)}
                            disabled={
                                interfaceOptions.transfer.length < 2 ||
                                !destination.zoneTransferInterface.server
                            }
                            onChange={(value) =>
                                updateTransferInterface({ type: 'interface', value })
                            }
                            error={interfaceError.transfer}
                        />
                    </div>
                </div>
            );
        case ACTION_NAMES.COPY_ROLES_TO_ZONES:
            return (
                <div>
                    <ReloadMultipleAutocomplete
                        fieldName={'zone'}
                        label={'Forward Zones'}
                        tags={destination['zoneList']}
                        onChange={(newValue) => onChange('zoneList', newValue)}
                        getOptions={getOptionsApi}
                    />

                    <ReloadMultipleAutocomplete
                        fieldName={'reverseZone'}
                        label={'Reverse Zones'}
                        tags={destination['reverseZoneList']}
                        onChange={(newValue) => onChange('reverseZoneList', newValue)}
                        getOptions={getOptionsApi}
                    />
                </div>
            );
    }
    return <div></div>;
}

export default DestinationForm;
