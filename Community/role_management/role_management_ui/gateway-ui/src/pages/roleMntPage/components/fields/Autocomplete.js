import React from 'react';
import { useState, useCallback, useEffect, useRef } from 'react';
import ComboBoxField from '../../pelagos-components/ComboBoxField';

function Autocomplete(props) {
    const inputRef = useRef(null);
    const { label, options, tag, onChange } = props;
    const [value, setValue] = useState(tag?.label || '');
    const [tempOptions, setTempOptions] = useState(options);

    const handleChange = (v) => {
        if (options.map((o) => o.value).includes(v.value)) {
            setTempOptions([]);
        }
        onChange(v);
    };

    const handleChangeText = (v, isSelect) => {
        if (!isSelect) setTempOptions(options);
        setValue(v);
    };

    const getSuggestions = useCallback(
        (text) => {
            return tempOptions.filter((v) => v.label.startsWith(text));
        },
        [tempOptions],
    );

    const renderSuggestion = (item, index) => {
        return <div key={index}>{item.label}</div>;
    };

    useEffect(() => {
        function handleClickComboBox() {
            setTempOptions(options);
        }
        const input = inputRef.current;
        input.addEventListener('click', handleClickComboBox);
        return () => input.removeEventListener('click', handleClickComboBox);
    }, []);

    return (
        <div>
            <ComboBoxField
                label={label}
                aria-label='Normal'
                getSuggestions={getSuggestions}
                id={`normal-combobox-${label}`}
                ref={inputRef}
                tag={tag}
                onChange={handleChange}
                onTextChange={handleChangeText}
                renderSuggestion={renderSuggestion}
                text={value}
                autoSelect={true}
            />
        </div>
    );
}

export default Autocomplete;
