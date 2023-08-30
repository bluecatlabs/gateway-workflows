import Select from './Select';
import useRandomId from './hooks/useRandomId';

import { Label, FieldError, FieldHelper } from '@bluecateng/pelagos';
import './DropDownField.less';

/** A dropdown field. */
const DropDownField = ({ id, className, label, helperText, error, ...props }) => {
    id = useRandomId(id);
    const labelId = `${id}-label`;
    const helperId = `${id}-helper`;
    const errorId = `${id}-error`;
    return (
        <div className={'DropDownField' + (className ? ' ' + className : '')}>
            <div className='DropDownField__label'>
                <Label id={labelId} text={label} />
            </div>
            <Select
                {...props}
                id={id}
                error={!!error}
                className='DropDownField__select'
                aria-labelledby={labelId}
                aria-describedby={error ? errorId : helperId}
            />
            {error ? (
                <FieldError id={errorId} text={error} />
            ) : (
                <FieldHelper id={helperId} text={helperText} />
            )}
        </div>
    );
};

export default DropDownField;
