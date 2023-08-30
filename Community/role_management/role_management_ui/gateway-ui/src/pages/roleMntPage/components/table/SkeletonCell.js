import React from 'react';
import './SkeletonCell.less';

function SkeletonCell(props) {
    return (
        <div className='cell-loading'>
            <div className='bar'></div>
        </div>
    );
}

export default SkeletonCell;
