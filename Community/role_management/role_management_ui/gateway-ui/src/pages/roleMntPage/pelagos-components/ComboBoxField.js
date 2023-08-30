// import TagInput from './TagInput';
import ComboBox from './ComboBox';
import { LabelLine, FieldError, FieldHelper } from '@bluecateng/pelagos';
import { forwardRef } from 'react';
import useRandomId from './hooks/useRandomId';
import './ComboBoxField.less';

/** A tag input field. */
const ComboBoxField = forwardRef(
    ({ id, className, label, optional, tag, helperText, error, ...props }, ref) => {
        id = useRandomId(id);
        const labelId = `${id}-label`;
        const helperId = `${id}-helper`;
        const errorId = `${id}-error`;
        return (
            <div className={`ComboBoxField${className ? ' ' + className : ''}`}>
                <LabelLine id={labelId} htmlFor={id} text={label} optional={optional && tag} />
                <ComboBox
                    {...props}
                    id={id}
                    ref={ref}
                    tag={tag}
                    error={error}
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
    },
);

export default ComboBoxField;
