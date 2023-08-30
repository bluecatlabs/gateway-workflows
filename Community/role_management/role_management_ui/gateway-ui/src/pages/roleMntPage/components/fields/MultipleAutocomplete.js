import React, { useState, useCallback, useEffect } from 'react';
import TagInputField from '../../pelagos-components/TagInputField';

function MultipleAutocomplete(props) {
    const { label, options, tags, onChange } = props;
    const [value, setValue] = useState('');

    const handleChangeText = (v) => {
        setValue(v);
    };

    const getSuggestions = useCallback(
        (text) => {
            return options.filter((option) => option.label.startsWith(text));
        },
        [options],
    );

    const renderSuggestion = (item, index) => {
        return <div key={index}>{item.label}</div>;
    };

    return (
        <div>
            <TagInputField
                label={label}
                tags={tags}
                onChange={onChange}
                onError={function noRefCheck() {}}
                validate={function noRefCheck() {}}
                aria-label='Normal'
                getSuggestions={getSuggestions}
                id='multiple-combobox'
                onTextChange={handleChangeText}
                renderSuggestion={renderSuggestion}
                text={value}
                autoSelect={true}
            />
        </div>
    );
}

export default MultipleAutocomplete;
