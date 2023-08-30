import React from 'react';
import { useState, useCallback, useEffect, useRef, useContext } from 'react';
import ComboBoxField from '../../pelagos-components/ComboBoxField';
import Icon from '../icons/Icon';
import AppContext from '../../AppContext';
import useDidMountEffect from '../../hooks/useDidMountEffect';

function ReloadAutocomplete(props) {
    const appContext = useContext(AppContext);
    const inputRef = useRef(null);
    const {
        fieldName,
        label,
        tag,
        onChange,
        getOptions,
        className,
        resetTextFlag,
        selectedOptions,
    } = props;
    const [selected, setSelected] = useState(false);
    const [value, setValue] = useState(tag?.label || '');

    const handleChange = (v, isSelect) => {
        if (isSelect) setSelected(true);
        onChange(v);
    };

    const handleChangeText = (v, isSelect) => {
        if (!isSelect) setSelected(false);
        setValue(v);
    };

    const getSuggestions = useCallback(
        async (text) => {
            if (selected) return [];
            if (getOptions) {
                const result = await getOptions({
                    config: appContext.config,
                    fieldName,
                    prefix: text,
                    selectedOptions,
                });
                return result;
            }
        },
        [selected, selectedOptions],
    );

    const renderSuggestion = (item, index) => {
        return (
            <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }}>
                {typeof item.value === 'object' && <Icon type={item.value.type} size='medium' />}
                <div key={index}>{item.label}</div>
            </div>
        );
    };

    useEffect(() => {
        function handleClickComboBox() {
            setSelected(false);
        }
        const input = inputRef.current;
        input.addEventListener('click', handleClickComboBox);
        return () => input.removeEventListener('click', handleClickComboBox);
    }, []);

    // in case: clear tag, clear text
    useDidMountEffect(() => {
        setValue('');
    }, [resetTextFlag]);

    return (
        <div className={className ? className : null}>
            <ComboBoxField
                label={label}
                aria-label='Normal'
                getSuggestions={getSuggestions}
                id={`reload-combobox-${label}`}
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

export default ReloadAutocomplete;
