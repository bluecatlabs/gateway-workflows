import { forwardRef } from 'react';

/** An item in IconMenu. */
const IconMenuItem = forwardRef(({ className, text, disabled, hasDivider, ...props }, ref) => (
    <li
        {...props}
        className={`IconMenu__option${disabled ? ' IconMenu--disabled' : ''}${
            hasDivider ? ' IconMenu--divider' : ''
        }${className ? ` ${className}` : ''}`}
        role='menuitem'
        ref={ref}>
        {text}
    </li>
));

export default IconMenuItem;
