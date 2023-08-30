import React, { useCallback, useContext, useState } from 'react';
import AppContext from '../../AppContext';
import TagInputField from '../../pelagos-components/TagInputField';
import Icon from '../icons/Icon';

function ReloadMultipleAutocomplete(props) {
    const appContext = useContext(AppContext);
    const { fieldName, filterField, label, getOptions, tags, onChange } = props;
    const [value, setValue] = useState('');

    const handleChangeText = (v) => {
        setValue(v);
    };

    const getSuggestions = useCallback(
        async (text) => {
            if (getOptions) {
                const result = await getOptions({
                    config: appContext.config,
                    fieldName,
                    prefix: text,
                    view: fieldName === 'zone' ? appContext.view : null,
                });

                // when filter zone, merge many zones with same absolute name
                if (filterField && fieldName === 'zone') {
                    function uniqByKeepFirst(a, key) {
                        let seen = new Set();
                        return a.filter((item) => {
                            let k = key(item);
                            return seen.has(k) ? false : seen.add(k);
                        });
                    }
                    return uniqByKeepFirst(result, (o) => o.label);
                }

                return result;
            }
        },
        [fieldName], // fieldName can be changed when changing zone type
    );

    const renderSuggestion = (item, index) => {
        if (item.value.forwarderZone && !filterField) {
            return (
                <div key={index}>
                    <Icon type={'Zone'} size='medium' />
                    <span style={{ paddingRight: '6px' }}>{item.label}</span>
                    {/* <span>{`(${item.value.viewName})`}</span> */}
                </div>
            );
        }
        return (
            <div key={index}>
                {typeof item.value === 'object' && <Icon type={item.value.type} size='medium' />}
                <span>{item.label}</span>
            </div>
        );
    };

    return (
        <div>
            <TagInputField
                label={label}
                filterField={filterField}
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

export default ReloadMultipleAutocomplete;
