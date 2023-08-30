import React, { useMemo } from 'react';
import './ActionResultTable.less';

import {
    Spinner,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
    TableScrollWrapper,
} from '@bluecateng/pelagos';
import { ACTION_RESULT_COLUMNS, DELETE_RESULT_COLUMNS } from '../../constants/table';
import { formatActionResult } from '../../processors/table';

function ActionResultTable(props) {
    const { isDeleteResult, data } = props;
    const columns = useMemo(
        () => (isDeleteResult ? DELETE_RESULT_COLUMNS : ACTION_RESULT_COLUMNS),
        [isDeleteResult],
    );
    return (
        <>
            <TableScrollWrapper className='ActionResultTableWrapper' tabIndex='-1'>
                <Table className='ActionResultTable' fixedLayout>
                    <TableHead>
                        <TableRow>
                            {columns.map(({ id, header, style }) => (
                                <TableHeader
                                    key={id + '_actionResult'}
                                    data-column={id + '_actionResult'}
                                    style={style}>
                                    {header}
                                </TableHeader>
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {data ? (
                            data
                                .map((row) => formatActionResult(row))
                                .map((item) => (
                                    <TableRow key={item.id}>
                                        {columns.map(({ id, value }) => (
                                            <TableCell key={id}>{value(item)}</TableCell>
                                        ))}
                                    </TableRow>
                                ))
                        ) : (
                            <TableRow style={{ borderBottom: 'none' }}></TableRow>
                        )}
                        {!data && (
                            <div className='ActionResultTable__spinningWrapper'>
                                <Spinner size='small' />
                            </div>
                        )}
                    </TableBody>
                </Table>
            </TableScrollWrapper>
        </>
    );
}

export default ActionResultTable;
