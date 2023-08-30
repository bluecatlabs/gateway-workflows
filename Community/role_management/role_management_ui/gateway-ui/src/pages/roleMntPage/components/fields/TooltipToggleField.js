import { ToggleField } from '@bluecateng/pelagos';
import { forwardRef } from 'react';
import setRefs from '../../pelagos-components/functions/setRefs';
import useTooltip from '../../pelagos-components/hooks/useTooltip';
import './TooltipToggleField.less';

const TooltipToggleField = forwardRef(
    (
        {
            id,
            icon,
            className,
            size = 'medium',
            type = 'ghost',
            tooltipText,
            tooltipPlacement = 'top',
            disabled,
            checked,
            onChange,
            ...props
        },
        ref,
    ) => {
        const tooltip = useTooltip(tooltipText, tooltipPlacement);
        const refs = ref ? setRefs(ref, tooltip) : tooltip;

        return (
            <div ref={refs} className='TooltipToggle'>
                <ToggleField value={checked} onChange={() => onChange(!checked)} />
            </div>
        );
    },
);

export default TooltipToggleField;
