import TagInput from './TagInput';
import { LabelLine, FieldError, FieldHelper } from '@bluecateng/pelagos';
import useRandomId from './hooks/useRandomId';

import './TagInputField.less';

/** A tag input field. */
const TagInputField = ({ id, className, label, optional, tags, helperText, error, ...props }) => {
    id = useRandomId(id);
    const labelId = `${id}-label`;
    const helperId = `${id}-helper`;
    const errorId = `${id}-error`;
    return (
        <div className={`TagInputField${className ? ' ' + className : ''}`}>
            <LabelLine
                id={labelId}
                htmlFor={id}
                text={label}
                optional={optional && tags.length === 0}
            />
            <TagInput
                {...props}
                id={id}
                tags={tags}
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
};

export default TagInputField;
