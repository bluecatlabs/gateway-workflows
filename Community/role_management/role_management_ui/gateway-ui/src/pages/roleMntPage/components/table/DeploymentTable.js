import React, { useEffect, useRef } from 'react';
import './DeploymentTable.less';

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
    TableScrollWrapper,
    TableTitle,
    Spinner,
    TableSelectAll,
    TableSelectRow,
} from '@bluecateng/pelagos';
import {
    DEPLOYMENT_OPTION_COLUMNS,
    DEPLOYMENT_OPTION_COLUMNS_WITH_INHERIT,
    TABLE_CELL_TOOLTIP_ID,
} from '../../constants/table';
import { formatDeploymentOption, getIdsDeployment } from '../../processors/table';
import { ACTION_NAMES } from '../../constants/action';

function DeploymentTable(props) {
    const { title, action, data, containInherited, total, selected, onChangeSelected, onDetail } =
        props;
    const tableWrapperRef = useRef(null);

    const columns = containInherited
        ? DEPLOYMENT_OPTION_COLUMNS_WITH_INHERIT
        : DEPLOYMENT_OPTION_COLUMNS;

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

    const handleClick = (id) => {
        const newSelected = { ...selected };
        if (newSelected[id]) newSelected[id] = false;
        else newSelected[id] = true;
        onChangeSelected(newSelected);
    };

    const allRowChecked = () => {
        if (total === 0) return false;
        const listID = getIdsDeployment(data);
        if (Array.isArray(listID)) {
            for (const id of listID) {
                if (!selected[id]) return false;
            }
        }
        return true;
    };

    const hasChecked = () => {
        const listID = getIdsDeployment(data);
        if (Array.isArray(listID)) {
            for (const id of getIdsDeployment(data)) {
                if (selected[id]) return true;
            }
        }
        return false;
    };

    const handleCheckAll = () => {
        if (allRowChecked()) {
            onChangeSelected({});
        } else {
            const newSelected = { ...selected };
            const listID = getIdsDeployment(data);
            if (Array.isArray(listID)) {
                for (const id of getIdsDeployment(data)) {
                    newSelected[id] = true;
                }
            }
            onChangeSelected(newSelected);
        }
    };

    return (
        <>
            <TableTitle title={title} />
            <TableScrollWrapper
                className='RoleMnt-deploymentTableWrapper'
                tabIndex='-1'
                ref={tableWrapperRef}>
                <Table className='RoleMnt-deploymentTable' fixedLayout>
                    <TableHead>
                        <TableRow>
                            {!onDetail && action.name == ACTION_NAMES.COPY_ROLES_TO_ZONES && (
                                <TableSelectAll
                                    aria-label='Select all rows'
                                    checked={allRowChecked()}
                                    indeterminate={hasChecked() && !allRowChecked()}
                                    onChange={handleCheckAll}
                                />
                            )}

                            {columns.map(({ id, header, style }) => (
                                <TableHeader
                                    key={id + '_deployment'}
                                    data-column={id + '_deployment'}
                                    style={style}>
                                    {header}
                                </TableHeader>
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {data ? (
                            data
                                .map((row) => formatDeploymentOption(row))
                                .map((item) => (
                                    <TableRow key={item.id}>
                                        {!onDetail &&
                                            action.name == ACTION_NAMES.COPY_ROLES_TO_ZONES && (
                                                <TableSelectRow
                                                    key={item.id + '_select'}
                                                    aria-label='Select row'
                                                    name='select'
                                                    checked={selected[item.id] ? true : false}
                                                    onChange={() => handleClick(item.id)}
                                                />
                                            )}

                                        {columns.map(({ id, value }) => (
                                            <TableCell key={id}>{value(item)}</TableCell>
                                        ))}
                                    </TableRow>
                                ))
                        ) : (
                            <TableRow style={{ borderBottom: 'none' }}></TableRow>
                        )}
                        {!data && (
                            <div className='RoleMnt-deploymentTable__spinningWrapper'>
                                <Spinner size='small' />
                            </div>
                        )}
                    </TableBody>
                </Table>
            </TableScrollWrapper>
        </>
    );
}

export default DeploymentTable;
