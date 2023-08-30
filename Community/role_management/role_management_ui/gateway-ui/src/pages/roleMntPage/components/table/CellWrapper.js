import React from 'react';
import './CellWrapper.less';
import SkeletonCell from './SkeletonCell';

function CellWrapper({ children, ...props }) {
    const { hasIcon, skeleton } = props;

    if (skeleton) return <SkeletonCell />;

    return (
        <div className={`Cellwrapper Cellwrapper--${hasIcon ? 'hasIcon' : 'textOnly'}`}>
            {children}
        </div>
    );
}

export default CellWrapper;
