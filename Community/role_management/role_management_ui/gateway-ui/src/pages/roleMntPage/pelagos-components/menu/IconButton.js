import { SvgIcon, ToggleField } from '@bluecateng/pelagos';
import { faAngleDown, faGear } from '@fortawesome/free-solid-svg-icons';
import { forwardRef } from 'react';
import setRefs from '../functions/setRefs';
import useTooltip from '../hooks/useTooltip';
import './IconButton.less';

/** An icon button. */
const IconButton = forwardRef(
    (
        {
            id,
            icon,
            className,
            size = 'medium',
            type = 'ghost',
            tooltipText,
            tooltipPlacement = 'right',
            disabled,
            onClick,
            ...props
        },
        ref,
    ) => {
        const tooltip = useTooltip(tooltipText, tooltipPlacement);
        const refs = ref ? setRefs(ref, tooltip) : tooltip;

        return disabled ? (
            <div
                {...props}
                id={id}
                className={`MenuIconButton MenuIconButton--${type}${
                    className ? ` ${className}` : ''
                }`}
                role='button'
                aria-disabled='true'
                style={{ display: 'flex', gap: '7px' }}
                ref={refs}>
                <SvgIcon style={{ width: '80px' }} icon={faGear} />
                <SvgIcon style={{ width: '80px' }} icon={faAngleDown} />
            </div>
        ) : (
            <button
                {...props}
                id={id}
                className={`MenuIconButton MenuIconButton--${type}${
                    className ? ` ${className}` : ''
                }`}
                type='button'
                ref={refs}
                style={{ display: 'flex', gap: '7px' }}
                onClick={onClick}>
                <SvgIcon style={{ width: '80px' }} icon={faGear} />
                <SvgIcon style={{ width: '80px' }} icon={faAngleDown} />
            </button>
        );
    },
);

export default IconButton;
