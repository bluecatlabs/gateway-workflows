import React, { useContext, useRef, useMemo } from 'react';
import './DeleteRoleConfirm.less';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
    TableScrollWrapper,
    Spinner,
    SvgIcon,
    IconMenu,
    IconMenuItem,
    DetailEntry,
    DetailsGrid,
    LabelLine,
} from '@bluecateng/pelagos';
import { DELETE_ACTION_CONFIRM_COLUMNS } from '../constants/table';
import { getActionPayload } from '../processors/common';
import { formatDataDeleteConfirm, getSelectedRoles } from '../processors/table';
import { getSelectedKeys } from '../utils/common';
import { faDownload } from '@fortawesome/free-solid-svg-icons';
import { migrateApi } from '../api';
import AppContext from '../AppContext';

const DeleteRoleConfirm = (props) => {
    const {
        selectedAction,
        roles,
        groupBy,
        selected,
        destination,
        validationData,
        onChangeHandlingAction,
    } = props;

    const selectedKeys = getSelectedKeys(selected);
    const deleteSelected = getSelectedRoles(roles, groupBy, selectedKeys);

    const items = validationData?.map((o, index) => ({
        message: o.message,
        status: o.status,
        id: index,
    }));
    const formatData = formatDataDeleteConfirm(deleteSelected);
    let data = [];
    for (let i = 0; i < items?.length; i++) {
        data.push({
            ...items[i],
            ...formatData[i],
        });
    }

    const appContext = useContext(AppContext);

    const confirmWrapperRef = useRef(null);

    const handleDownloadXml = () => {
        if (validationData?.some((o) => o.status === 'UNAVAILABLE')) return;
        const selectedKeys = getSelectedKeys(selected);
        const actionPayload = getActionPayload({
            selectedAction,
            groupBy,
            roles,
            selected: selectedKeys,
            destination,
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

    return (
        <div className='confirmWrapper' ref={confirmWrapperRef}>
            <div className='dowloadIcon' onClick={handleDownloadXml}>
                <IconMenu
                    id='downloadButton'
                    icon={faDownload}
                    disabled={validationData?.some((o) => o.status === 'UNAVAILABLE')}
                    tooltipText={`Download Migration XML`}
                    tooltipPlacement='top'
                    aria-label={`Download Migration XML`}>
                    <IconMenuItem />
                </IconMenu>
            </div>
            <TableScrollWrapper className='DeleteConfirmTableWrapper' tabIndex='-1'>
                <Table className='DeleteConfirmTable' stickyHeader fixedLayout>
                    <TableHead>
                        <TableRow>
                            {DELETE_ACTION_CONFIRM_COLUMNS.map(({ id, header, style }) => (
                                <TableHeader key={id + '_actionChange'} style={style}>
                                    {header}
                                </TableHeader>
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {data ? (
                            data.map((item, index) => (
                                <TableRow>
                                    {DELETE_ACTION_CONFIRM_COLUMNS.map(({ value }) => (
                                        <TableCell>{value(item)}</TableCell>
                                    ))}
                                </TableRow>
                            ))
                        ) : (
                            <TableRow></TableRow>
                        )}
                        {!data && (
                            <div className='ActionResultTable__spinningWrapper'>
                                <Spinner size='small' />
                            </div>
                        )}
                    </TableBody>
                </Table>
            </TableScrollWrapper>
        </div>
    );
};

export default DeleteRoleConfirm;
