import React, { useRef, useState } from 'react';
import './CellContentWrapper.less';
import { createPortal } from 'react-dom';
import { TABLE_CELL_TOOLTIP_ID } from '../../constants/table';

function CellContentWrapper(props) {
    const { content } = props;
    const contentRef = useRef(null);
    const tooltipRef = useRef(null);

    const [showTooltip, setShowTooltip] = useState(false);
    const [tooltipPosition, setTooltipPosition] = useState({ top: '0px', left: '0px' });

    const handleHover = () => {
        if (contentRef.current.offsetWidth >= contentRef.current.scrollWidth) return;
        const { top, left, right } = contentRef.current.getBoundingClientRect();
        setTooltipPosition({ top: `${top - 2}px`, left: `${Math.round((left + right) / 2)}px` });
        setShowTooltip(true);
    };

    const handleMouseLeave = () => {
        if (contentRef.current.offsetWidth >= contentRef.current.scrollWidth) return;
        setShowTooltip(false);
        if (tooltipRef.current) tooltipRef.current.remove();
    };

    return (
        <span
            ref={contentRef}
            className='Cellcontent'
            onMouseOver={handleHover}
            onMouseLeave={handleMouseLeave}>
            {content}
            {showTooltip &&
                createPortal(
                    <div
                        id={TABLE_CELL_TOOLTIP_ID}
                        className='Cellcontent-tooltip'
                        style={{
                            ...tooltipPosition,
                        }}
                        ref={tooltipRef}>
                        {content}
                    </div>,
                    document.body,
                )}
        </span>
    );
}

export default CellContentWrapper;
