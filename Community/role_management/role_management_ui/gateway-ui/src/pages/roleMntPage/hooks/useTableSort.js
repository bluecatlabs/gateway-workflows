// Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
import { useCallback, useMemo, useState } from 'react';

export default (initialSortKey, initialSortOrder, getComparator, data) => {
    const [sortKey, setSortKey] = useState(initialSortKey);
    const [sortOrder, setSortOrder] = useState(initialSortOrder);

    const handleHeaderClick = useCallback(
        ({ target }) => {
            const th = target.closest('th');
            const column = th?.dataset?.column;
            if (column && getComparator(column)) {
                if (sortKey === column) {
                    setSortOrder(sortOrder === 'a' ? 'd' : 'a');
                } else {
                    setSortKey(column);
                    setSortOrder('a');
                }
            }
        },
        [sortKey, sortOrder],
    );

    const sortedData = useMemo(() => {
        const comparator = getComparator(sortKey);
        const modifier = sortOrder === 'a' ? 1 : -1;
        return data && [...data].sort((a, b) => comparator(a, b) * modifier);
    }, [data, getComparator, sortKey, sortOrder]);

    return [sortKey, sortOrder, sortedData, handleHeaderClick];
};
