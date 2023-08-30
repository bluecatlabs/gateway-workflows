import React, { useContext, useEffect, useMemo, useRef, useState } from 'react';
import './Confirm.less';

import {
    DetailEntry,
    IconMenu,
    IconMenuItem,
    LabelLine,
    SvgIcon,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
    TableScrollWrapper,
} from '@bluecateng/pelagos';
import { faArrowRight, faDownload } from '@fortawesome/free-solid-svg-icons';
import { getDeploymentOptionApi, migrateApi, getServerByInterface } from '../api';
import AppContext from '../AppContext';
import { ACTION_NAMES } from '../constants/action';
import { ACTION_AFTER_CHANGE_COLUMNS, ACTION_BEFORE_CHANGE_COLUMNS } from '../constants/table';
import { getActionPayload, getDeploymentOptionParam } from '../processors/common';
import { formatValidationData } from '../processors/table';
import { getSelectedKeys, setElementBackgroundColor } from '../utils/common';
import Icon from './icons/Icon';
import DeploymentTable from './table/DeploymentTable';

const BACKGROUND_COLOR = {
    enter: '#e4e9f1',
    leave: '#f2f4f8',
    enterSelected: '#cdd3da',
    leaveSelected: '#dde1e6',
};

function Confirm(props) {
    const {
        selectedAction,
        selected,
        destination,
        validationData,
        groupBy,
        view,
        roles,
        onChangeHandlingAction,
        handleGetDeploymentDataFromDialog,
        handleGetOptionDNS,
    } = props;

    const data = useMemo(() => {
        const items = validationData.map((o, index) => ({ ...o['role'], id: index }));
        return formatValidationData({ items, target: 'role' });
    }, [validationData]);

    const dataChanged = useMemo(() => {
        const items = validationData.map((o, index) => ({
            ...o['new_role'],
            message: o.message,
            status: o.status,
            id: index,
        }));
        return formatValidationData({ items, target: 'new_role' });
    }, [validationData]);

    const appContext = useContext(AppContext);
    const syncTable = selectedAction.name !== ACTION_NAMES.COPY_ROLES_TO_ZONES;

    const confirmWrapperRef = useRef(null);
    const tableLeftRef = useRef(null);
    const tableRightRef = useRef(null);
    const tableWrapperRef = useState(null);

    const [selectedRow, setSelectedRow] = useState(0);
    const [selectedPosition, setSelectedPosition] = useState('left');

    const handleGetInitialServer = () => {
        if (!destination.serverInterface.server.value) {
            getServerByInterface({ config: appContext.config, hint: dataChanged[0].interface })
                .then((res) => {
                    setDeploymentOptionSelected({
                        ...deploymentOptionSelected,
                        deploymentOptionParam: {
                            ...deploymentOptionSelected.deploymentOptionParam,
                            server: res.data[0].server.name,
                        },
                    });
                })
                .catch((error) => console.log(error));
        }
    };

    const [deploymentOptionSelected, setDeploymentOptionSelected] = useState({
        roleId: data[0].id,
        deploymentOptionParam: getDeploymentOptionParam({
            config: appContext.config,
            role: data[0],
            fromDeploymentOptionData: true,
            server: destination.serverInterface.server.value,
        }),
    });
    const [deploymentData, setDeploymentData] = useState(null);
    const [deploymentTotal, setDeploymentTotal] = useState(null);

    const [deploymentSelected, setDeploymentSelected] = useState({});

    const handleScrollFirst = (scroll) => {
        tableRightRef.current.scrollTop = scroll.target.scrollTop;
    };
    const handleScrollSecond = (scroll) => {
        tableLeftRef.current.scrollTop = scroll.target.scrollTop;
    };

    const handleMouseEvent = ({ eventType, item }) => {
        const leftE = document.getElementById(item.id + '_left');
        const rightE = document.getElementById(item.id + '_right');
        const eventKey =
            leftE.ariaSelected === 'true' || rightE.ariaSelected === 'true'
                ? eventType === 'leave'
                    ? 'leaveSelected'
                    : 'enterSelected'
                : eventType;

        leftE.style.backgroundColor = BACKGROUND_COLOR[eventKey];
        rightE.style.backgroundColor = BACKGROUND_COLOR[eventKey];
    };

    const handleClickRow = ({ item, position }) => {
        setSelectedRow(item.id);
        setSelectedPosition(position);

        if (destination.serverInterface.server.value) {
            setDeploymentOptionSelected({
                roleId: item.id,
                deploymentOptionParam: getDeploymentOptionParam({
                    config: appContext.config,
                    server: destination.serverInterface.server.value,
                    role: item,
                    fromDeploymentOptionData: true,
                }),
            });
        } else {
            getServerByInterface({ config: appContext.config, hint: item.interface })
                .then((res) => {
                    setDeploymentOptionSelected({
                        roleId: item.id,
                        deploymentOptionParam: getDeploymentOptionParam({
                            config: appContext.config,
                            server: res.data[0].server.name,
                            role: item,
                            fromDeploymentOptionData: true,
                        }),
                    });
                })
                .catch((error) => console.log(error));
        }

        for (let i = 1; i < data.length + 1; i++) {
            if (i !== item.id) {
                setElementBackgroundColor(i + '_left', BACKGROUND_COLOR['leave']);
                setElementBackgroundColor(i + '_right', BACKGROUND_COLOR['leave']);
            }
        }
    };

    const disableDownloadButton = validationData.some(
        (x) => x.status !== 'AVAILABLE' && x.status !== 'WARNING' && x.status !== 'INFO',
    );

    const handleDownloadXml = () => {
        if (disableDownloadButton) return;
        const selectedKeys = getSelectedKeys(selected);
        const optionSelected = getSelectedKeys(deploymentSelected);
        const actionPayload = getActionPayload({
            selectedAction,
            groupBy,
            roles,
            selected: selectedKeys,
            destination,
            view,
            deploymentData,
            optionSelected,
        });

        let filename = '';
        onChangeHandlingAction(true);
        migrateApi({ config: appContext.config, selectedAction, actionPayload })
            .then((res) => {
                const header = res.headers.get('Content-Disposition');
                filename = header?.split('filename=')[1].split('"')[1];

                return res.blob();
            })
            .then((blob) => {
                onChangeHandlingAction(false);

                const element = document.createElement('a');
                element.style.cssText = 'position:fixed;top:0;z-index:999;';
                const file = new Blob([blob]);

                element.href = URL.createObjectURL(file);
                element.download = filename;
                confirmWrapperRef.current.appendChild(element);
                element.click();
                element.parentNode.removeChild(element);
            })
            .catch((error) => {
                console.log(error);
                onChangeHandlingAction(false);
            });
    };
    const getDeploymentOptions = () => {
        if (!deploymentOptionSelected?.deploymentOptionParam) return;
        setDeploymentData(null);
        getDeploymentOptionApi(deploymentOptionSelected?.deploymentOptionParam)
            .then((res) => {
                setDeploymentData(res?.data);
                setDeploymentTotal(res?.count);
                handleGetDeploymentDataFromDialog(res?.data);
            })
            .catch((error) => console.log(error));
    };

    useEffect(() => {
        const changedTableHeight = data.length >= 5 ? 194 : (data.length + 1) * 32;
        tableWrapperRef.current.style.height = `${changedTableHeight}px`;
    }, []);

    useEffect(() => {
        handleGetInitialServer();
    }, []);

    useEffect(() => {
        getDeploymentOptions();
    }, [deploymentOptionSelected]);

    const CustomRow = (props) => {
        const { item, selected, position } = props;
        const columns =
            position === 'left' ? ACTION_BEFORE_CHANGE_COLUMNS : ACTION_AFTER_CHANGE_COLUMNS;
        return (
            <TableRow
                id={item.id + '_' + position}
                key={item.id}
                selected={selected}
                onMouseEnter={() => handleMouseEvent({ eventType: 'enter', item })}
                onMouseLeave={() => handleMouseEvent({ eventType: 'leave', item })}
                onClick={() => handleClickRow({ item, position })}>
                {columns.map(({ value }) => (
                    <TableCell>{value(item)}</TableCell>
                ))}
            </TableRow>
        );
    };

    const handleShowDestination = (destination) => {
        const singleObj = (arr) => arr.length === 1;

        if (destination.serverInterface.interface.name) {
            return (
                <div className='MultipleFieldsWrapper'>
                    <DetailEntry
                        label='Server'
                        className='DestinationObjects__first'
                        value={
                            <div className='IconValueWrapper'>
                                <Icon type='Server' size='small' />
                                {destination.serverInterface.server.label}
                            </div>
                        }
                    />
                    <DetailEntry
                        label='Server Interface'
                        className='DestinationObjects__second'
                        value={
                            <div className='IconValueWrapper'>
                                <Icon type='Interface' size='small' />
                                {destination.serverInterface.interface.name}
                            </div>
                        }
                    />
                </div>
            );
        } else if (destination.zoneList.length > 0 || destination.reverseZoneList.length > 0) {
            return (
                <div style={{ marginLeft: '16px' }}>
                    <LabelLine
                        text={`Zone${
                            singleObj(destination.zoneList.concat(destination.reverseZoneList))
                                ? ''
                                : 's'
                        }`}
                    />
                    <div className='MultipleValuesWrapper'>
                        {destination.zoneList.map((item) => (
                            <div className='icon-value'>
                                <Icon type='Zone' size='small' />
                                <div>{item.label} </div>
                            </div>
                        ))}
                        {destination.reverseZoneList.map((item) => (
                            <div className='icon-value'>
                                <Icon type={item.value.type} size='small' />
                                <div>{item.label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            );
        } else if (destination.serverInterfaceList.length > 0) {
            return (
                <div>
                    <div style={{ marginLeft: '16px' }}>
                        <LabelLine
                            text={`Interface${
                                singleObj(destination.serverInterfaceList) ? '' : 's'
                            }`}
                        />
                        <div className='MultipleValuesWrapper MultipleValuesWrapper--noMarginBottom'>
                            {destination.serverInterfaceList.map((item) => (
                                <div className='icon-value'>
                                    <Icon type='Interface' size='small' />
                                    <div>{`${item.server.value} [${item.serverInterface.name}]`}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className='MultipleFieldsWrapper'>
                        <DetailEntry
                            label='Role Type'
                            className='DestinationObjects__first'
                            value={destination.roleType.label}
                        />
                        {destination.zoneTransferInterface.server.value && (
                            <DetailEntry
                                label='Zone Transfer Interface'
                                className='DestinationObjects__second'
                                value={
                                    <div className='IconValueWrapper'>
                                        <Icon type='Interface' size='small' />
                                        {`${destination.zoneTransferInterface.server.value} [${destination.zoneTransferInterface.interface.name}]`}
                                    </div>
                                }
                            />
                        )}
                    </div>
                </div>
            );
        } else {
            return null;
        }
    };

    return (
        <div className='confirmWrapper' ref={confirmWrapperRef}>
            {handleShowDestination(destination)}
            <div className='tableChangeWrapper' ref={tableWrapperRef}>
                <div className='dowloadIcon' onClick={handleDownloadXml}>
                    <IconMenu
                        id='downloadButton'
                        icon={faDownload}
                        disabled={disableDownloadButton}
                        tooltipText={`Download Migration XML`}
                        tooltipPlacement='top'
                        aria-label={`Download Migration XML`}>
                        <IconMenuItem />
                    </IconMenu>
                </div>

                <TableScrollWrapper
                    onScroll={handleScrollFirst}
                    ref={tableLeftRef}
                    className='actionChangeTable__tableWrapper leftTableWrapper'
                    tabIndex='-1'>
                    <Table className='actionChangeTable__table' stickyHeader fixedLayout>
                        <TableHead>
                            <TableRow>
                                {ACTION_BEFORE_CHANGE_COLUMNS.map(({ id, header, style }) => (
                                    <TableHeader key={id + '_actionChange'} style={style}>
                                        {header}
                                    </TableHeader>
                                ))}
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {data.map((item, index) => (
                                <CustomRow
                                    item={item}
                                    selected={
                                        item.id === selectedRow
                                        // (selectedPosition === 'left' || syncTable)
                                    }
                                    position={'left'}
                                />
                            ))}
                        </TableBody>
                    </Table>
                </TableScrollWrapper>

                <div className='arrowIcon'>
                    <SvgIcon icon={faArrowRight} />
                </div>

                <TableScrollWrapper
                    onScroll={handleScrollSecond}
                    ref={tableRightRef}
                    className='actionChangeTable__tableWrapper'
                    tabIndex='-1'>
                    <Table className='actionChangeTable__table' stickyHeader fixedLayout>
                        <TableHead>
                            <TableRow>
                                {ACTION_AFTER_CHANGE_COLUMNS.map(({ id, header, style }) => (
                                    <TableHeader key={id + '_actionChange'} style={style}>
                                        {header}
                                    </TableHeader>
                                ))}
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {dataChanged.map((item, index) => (
                                <CustomRow
                                    item={item}
                                    selected={
                                        item.id === selectedRow
                                        // (selectedPosition === 'right' || syncTable)
                                    }
                                    position={'right'}
                                />
                            ))}
                        </TableBody>
                    </Table>
                </TableScrollWrapper>
            </div>

            <div className='deploymentWrapper'>
                <DeploymentTable
                    title='DNS Deployment Options'
                    action={selectedAction}
                    data={deploymentData}
                    total={deploymentTotal}
                    selected={deploymentSelected}
                    onChangeSelected={(newSelected) => {
                        setDeploymentSelected(newSelected);
                        handleGetOptionDNS(newSelected);
                    }}
                />
            </div>
        </div>
    );
}

export default Confirm;
