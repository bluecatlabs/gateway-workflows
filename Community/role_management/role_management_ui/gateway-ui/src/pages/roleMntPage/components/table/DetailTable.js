import React, { useContext, useRef, useEffect, useState, useMemo } from 'react';
import './DetailTable.less';

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
    TableScrollWrapper,
    TableTitle,
    DetailEntry,
    DetailsGrid,
} from '@bluecateng/pelagos';
import {
    DEFAULT_COLUMNS_WITH_INHERIT,
    DETAIL_COLUMNS_OBJECT,
    DETAIL_COLUMNS_OBJECT_INHERIT,
    DETAIL_NO_GROUP_COLUMNS,
    DETAIL_NO_GROUP_COLUMNS_WITH_INHERIT,
    TABLE_CELL_TOOLTIP_ID,
} from '../../constants/table';
import { formatRole } from '../../processors/table';
import { getDeploymentOptionParam } from '../../processors/common';
import { ROLE_TYPE_LABELS } from '../../constants/action';
import Icon from '../icons/Icon';
import AppContext from '../../AppContext';
import { getParentByType } from '../../api';
import { getDetailTableColumns } from '../../utils/common';

function DetailTable(props) {
    const appContext = useContext(AppContext);
    const {
        title,
        data,
        groupBy,
        containInherited,
        groupObjSelected,
        serverInterfaceId,
        hasMultipleZones,
        deploymentOptionSelected,
        onChangeSelected,
    } = props;
    const tableWrapperRef = useRef(null);
    const [parentServer, setParentServer] = useState('');
    const [parentServerList, setParentServerList] = useState({});

    let items = data.map((role) => formatRole(role));
    const columns = useMemo(
        () => getDetailTableColumns(groupBy, containInherited),
        [groupBy, containInherited],
    );

    const listServerInterfaceId = data.map((obj) => obj.serverInterface.id);
    items.map((obj) => {
        obj.parentServer = parentServerList[`${obj.serverInterfaceId.toString()}`]?.name;
    });

    const handleClick = (item) => {
        if (!hasMultipleZones) return;
        const role = data.filter((o) => o.id === item.id)[0];
        onChangeSelected({
            roleId: role.id,
            deploymentOptionParam: getDeploymentOptionParam({
                config: appContext.config,
                role,
            }),
        });
    };

    const rowSelected = (item) => {
        return item.id === deploymentOptionSelected.roleId;
    };

    const getParentServer = () => {
        if (!serverInterfaceId) return;
        getParentByType('servers', serverInterfaceId)
            .then((data) => {
                setParentServer(data[`${serverInterfaceId}`].name);
            })
            .catch((error) => {
                console.log(error);
            });
    };

    const getParentServerList = () => {
        getParentByType('servers', listServerInterfaceId.join(','))
            .then((data) => {
                setParentServerList(data);
            })
            .catch((error) => {
                console.log(error);
            });
    };

    useEffect(() => {
        getParentServer();
    }, [serverInterfaceId]);

    useEffect(() => {
        getParentServerList();
    }, [data]);

    useEffect(() => {
        const handleScroll = (e) => {
            const tooltipEl = document.getElementById(TABLE_CELL_TOOLTIP_ID);
            if (tooltipEl) tooltipEl.remove();
        };
        tableWrapperRef.current.addEventListener('scroll', handleScroll);

        return () => {
            tableWrapperRef.current.removeEventListener('scroll', handleScroll);
        };
    }, []);

    const renderGroupItem = () => {
        switch (groupBy.value) {
            case 'zone':
                const jsGroupObj = JSON.parse(groupObjSelected);
                const type = jsGroupObj.type;
                const iconZoneType = type.includes('Block')
                    ? 'Block'
                    : type.includes('Network')
                    ? 'Network'
                    : type;

                return (
                    <DetailsGrid className='GroupObjects'>
                        <DetailEntry
                            label='View'
                            className='GroupObjects__first'
                            value={
                                <div className='IconValueWrapper'>
                                    <Icon type='View' size='small' />
                                    {jsGroupObj.viewName}
                                </div>
                            }
                        />
                        {jsGroupObj.name && (
                            <DetailEntry
                                label='Zone'
                                className='GroupObjects__second'
                                value={
                                    <div className='IconValueWrapper'>
                                        <Icon type={iconZoneType} size='small' />
                                        {jsGroupObj.name}
                                    </div>
                                }
                            />
                        )}
                    </DetailsGrid>
                );
            case 'role':
                return (
                    <DetailsGrid className='GroupObjects'>
                        <DetailEntry
                            label='Role'
                            className='GroupObjects__first'
                            value={ROLE_TYPE_LABELS[groupObjSelected]}
                        />
                    </DetailsGrid>
                );
            case 'server':
                return (
                    <DetailsGrid className='GroupObjects'>
                        <DetailEntry
                            label='Server'
                            className='GroupObjects__first'
                            value={
                                <div className='IconValueWrapper'>
                                    <Icon type='Server' size='small' />
                                    {parentServer}
                                </div>
                            }
                        />
                        <DetailEntry
                            label='Server Interface'
                            className='GroupObjects__second'
                            value={
                                <div className='IconValueWrapper'>
                                    <Icon type='Interface' size='small' />
                                    {groupObjSelected}
                                </div>
                            }
                        />
                    </DetailsGrid>
                );

            case 'role_server':
                return (
                    <DetailsGrid className='GroupObjects'>
                        <DetailEntry
                            label='Server'
                            className='GroupObjects__first'
                            value={
                                <div className='IconValueWrapper'>
                                    {parentServer && <Icon type='Server' size='small' />}
                                    {parentServer}
                                </div>
                            }
                        />
                        <DetailEntry
                            label='Server Interface'
                            className='GroupObjects__second'
                            value={
                                <div className='IconValueWrapper'>
                                    <Icon type='Interface' size='small' />
                                    {JSON.parse(groupObjSelected).server}
                                </div>
                            }
                        />
                        <DetailEntry
                            label='Role'
                            className='GroupObjects__third'
                            value={ROLE_TYPE_LABELS[JSON.parse(groupObjSelected).role]}
                        />
                    </DetailsGrid>
                );
            default:
        }
    };

    return (
        <div>
            <TableTitle title={title} />
            {renderGroupItem()}
            <TableScrollWrapper
                className='RoleMnt-detailTableWrapper'
                tabIndex='-1'
                ref={tableWrapperRef}>
                <Table className='RoleMnt-detailTable' fixedLayout>
                    <TableHead>
                        <TableRow>
                            {columns?.map(({ id, header, style }) => (
                                <TableHeader
                                    key={id + '_detail'}
                                    data-column={id + '_detail'}
                                    style={style}>
                                    {header}
                                </TableHeader>
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {items.map((item, index) => (
                            <TableRow
                                key={item.id}
                                style={{ cursor: hasMultipleZones ? 'pointer' : 'default' }}
                                selected={rowSelected(item, index)}
                                onClick={() => handleClick(item)}>
                                {columns?.map(({ id, value }) => (
                                    <TableCell key={id}>{value(item)}</TableCell>
                                ))}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableScrollWrapper>
        </div>
    );
}

export default DetailTable;
