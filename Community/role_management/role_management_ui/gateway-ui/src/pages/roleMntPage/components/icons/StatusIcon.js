import { SvgIcon } from '@bluecateng/pelagos';
import { forwardRef } from 'react';
import setRefs from '../../pelagos-components/functions/setRefs';
import useTooltip from '../../pelagos-components/hooks/useTooltip';
import './StatusIcon.less';
import { faCheck, faXmark, faWarning, faInfoCircle } from '@fortawesome/free-solid-svg-icons';

const StatusIcon = forwardRef(
    (
        { id, className, size = 'medium', status, tooltipText, tooltipPlacement = 'top', ...props },
        ref,
    ) => {
        const tooltip = useTooltip(tooltipText, tooltipPlacement);
        const refs = ref ? setRefs(ref, tooltip) : tooltip;
        return (
            <span
                {...props}
                id={id}
                className={`StatusIcon StatusIcon--${size} StatusIcon--${status}${
                    className ? ` ${className}` : ''
                }`}
                ref={refs}>
                {status === 'success' && <SvgIcon icon={faCheck} />}
                {status === 'fail' && <SvgIcon icon={faXmark} />}
                {status === 'warning' && <SvgIcon icon={faWarning} />}
                {status === 'info' && <SvgIcon icon={faInfoCircle} />}
            </span>
        );
    },
);

export default StatusIcon;
