import {
    Layer,
    Spinner,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
    TableScrollWrapper,
    TableSelectAll,
    TableSelectRow,
} from '@bluecateng/pelagos';
import { forwardRef, useCallback, useContext, useEffect, useState } from 'react';
import useTableSort from '../../hooks/useTableSort';

import { getRolesApi } from '../../api';
import AppContext from '../../AppContext';
import { TABLE_CELL_TOOLTIP_ID } from '../../constants/table';
import { formatRoleList, getIds } from '../../processors/table';
import './LazyLoadTable.less';

const LazyLoadTable = forwardRef((props, ref) => {
    const appContext = useContext(AppContext);
    const {
        roles,
        total,
        firstLoadingTable,
        pageSize,
        columns,
        onChangeRoles,
        handleClickDetail,
        rowSelected,
        selected,
        onChangeSelected,
        groupBy,
        filter,
        containInherited,
        pagination,
        onChangePagination,
    } = props;

    const [fetchingData, setFetchingData] = useState(false);

    const getData = () => {
        setFetchingData(true);

        getRolesApi({
            config: appContext.config,
            view: appContext.view,
            groupBy,
            containInherited,
            filter,
            pagination,
        })
            .then((res) => {
                if (res.total > 0) {
                    const result = res.data;
                    if (roles.find((o) => o.id === result[0]?.id)) {
                    } else {
                        const newPagination = {
                            start: pagination.start + pageSize,
                        };
                        onChangePagination(newPagination);
                        onChangeRoles([...roles, ...result]);
                    }
                }
            })
            .catch((error) => console.log(error))
            .finally(() => setFetchingData(false));
    };

    useEffect(() => {
        const handleScroll = (e) => {
            const table = e.target;

            if (
                Math.abs(table.scrollHeight - table.scrollTop - table.clientHeight) <= 3.0 &&
                pagination.start <= total - 1 &&
                !fetchingData
            ) {
                getData();
            }

            const tooltipEl = document.getElementById(TABLE_CELL_TOOLTIP_ID);
            if (tooltipEl) tooltipEl.remove();
        };

        ref.current.addEventListener('scroll', handleScroll);

        return () => {
            ref.current.removeEventListener('scroll', handleScroll);
        };
    }, [fetchingData, pagination, total]);
    // because initial total = 0

    const handleClick = (id) => {
        const newSelected = { ...selected };
        if (newSelected[id]) newSelected[id] = false;
        else newSelected[id] = true;
        onChangeSelected(newSelected);
    };

    const allRowChecked = () => {
        if (total === 0) return false;
        for (const id of getIds(roles, groupBy)) {
            if (!selected[id]) return false;
        }
        return true;
    };

    const hasChecked = () => {
        for (const id of getIds(roles, groupBy)) {
            if (selected[id]) return true;
        }
        return false;
    };

    const handleCheckAll = () => {
        if (allRowChecked()) {
            onChangeSelected({});
        } else {
            const newSelected = { ...selected };
            for (const id of getIds(roles, groupBy)) {
                newSelected[id] = true;
            }
            onChangeSelected(newSelected);
        }
    };

    const getComparator = useCallback(
        (key) => {
            const col = columns.find(({ id }) => id === key);
            return col ? col.comparator : () => {};
        },
        [columns],
    );

    const [sortKey, sortOrder, sortedItems, handleHeaderClick] = useTableSort(
        null,
        null,
        getComparator,
        formatRoleList(roles, groupBy),
    );

    const handleSort = (target) => {
        handleHeaderClick(target);
    };

    const renderFooter = () => {
        return (
            <Layer className='LazyLoadTable__footer'>
                <div className='LazyLoadTableFooter__total'>{`${sortedItems.length} of ${total} item(s) loaded`}</div>

                {fetchingData && (
                    <div className='LazyLoadTableFooter__loading'>
                        <span>.</span>
                        <Spinner size='tiny' />
                    </div>
                )}
            </Layer>
        );
    };

    return (
        <div className='LazyLoadTable'>
            <TableScrollWrapper className='LazyLoadTable__tableWrapper' ref={ref} tabIndex='-1'>
                <Table className='LazyLoadTable__table' stickyHeader fixedLayout>
                    <TableHead>
                        <TableRow onClick={handleSort}>
                            <TableSelectAll
                                aria-label='Select all rows'
                                checked={allRowChecked()}
                                indeterminate={hasChecked() && !allRowChecked()}
                                onChange={handleCheckAll}
                            />
                            {columns.map(({ id, header, comparator, style }) => (
                                <TableHeader
                                    key={id}
                                    sortable={!!comparator}
                                    sortOrder={sortKey === id ? sortOrder : null}
                                    style={style}
                                    data-column={id}>
                                    {header}
                                </TableHeader>
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {sortedItems.map((item) => {
                            const { id: rowId } = item;
                            return (
                                <TableRow key={rowId} selected={rowSelected(item)}>
                                    <TableSelectRow
                                        key={rowId + '_select'}
                                        aria-label='Select row'
                                        name='select'
                                        checked={selected[item.id] ? true : false}
                                        onChange={() => handleClick(item.id)}
                                    />
                                    {columns.map(({ id, value }) => (
                                        <TableCell key={id} onClick={() => handleClickDetail(item)}>
                                            {value(item)}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
                {/* {roles.length > 0 && !firstLoadingTable && total + 2 < pageSize && renderFooter()} */}
                {/* {roles.length > 0 && !firstLoadingTable && renderFooter()} */}
            </TableScrollWrapper>

            {/* {roles.length > 0 && !firstLoadingTable && total + 2 >= pageSize && renderFooter()} */}
            {roles.length > 0 && !firstLoadingTable && renderFooter()}
        </div>
    );
});

export default LazyLoadTable;
