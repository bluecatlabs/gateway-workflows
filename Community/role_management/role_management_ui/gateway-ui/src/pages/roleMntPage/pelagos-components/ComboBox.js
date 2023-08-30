import { IconButton, Layer } from '@bluecateng/pelagos';
import { faPlus } from '@fortawesome/free-solid-svg-icons';
import debounce from 'lodash-es/debounce';
import { cloneElement, useCallback, useEffect, useMemo, useRef, useState, forwardRef } from 'react';
import { createPortal } from 'react-dom';
import Icon from '../components/icons/Icon';
import './ComboBox.less';
import scrollToItem from './functions/scrollToItem';

/** A combination box of a text field and an autocomplete list. */
const ComboBox = forwardRef(
    (
        {
            id,
            autoSelect,
            tag,
            onChange,
            text,
            error,
            getSuggestions,
            renderSuggestion,
            onTextChange,
            ...props
        },
        ref,
    ) => {
        const buttonRef = useRef(null);
        const listRef = useRef(null);
        const mounted = useRef(false);

        const [suggestions, setSuggestions] = useState([]);
        const [open, setOpen] = useState(false);
        const [selected, setSelected] = useState(-1);

        const debouncedChange = useMemo(
            (v) => debounce((v) => (onTextChange(v), onChange('')), 33),
            [onTextChange, onChange],
        );

        const hideList = useCallback(
            () => (setSuggestions([]), setOpen(false), setSelected(-1)),
            [],
        );

        const updateSuggestions = useMemo(
            () =>
                debounce(
                    (text) =>
                        Promise.resolve(getSuggestions(text)).then((suggestions) => {
                            if (suggestions.length === 0) {
                                hideList();
                            } else {
                                setSuggestions(suggestions);
                                setOpen(true);
                                setSelected(autoSelect ? 0 : -1);
                            }
                        }),
                    150,
                ),
            [hideList, autoSelect, getSuggestions],
        );
        const selectSuggestion = useCallback(
            (index) => (
                hideList(),
                onChange(suggestions[index], true),
                onTextChange(suggestions[index].label, true)
            ),
            [suggestions, hideList, onChange, onTextChange],
        );

        const handleKeyDown = useCallback(
            (event) => {
                switch (event.keyCode) {
                    case 13: // enter
                        event.preventDefault();
                        if (selected !== -1) {
                            selectSuggestion(selected);
                        }
                        break;
                    case 27: // escape
                        event.preventDefault();
                        debouncedChange.cancel();
                        hideList();
                        onTextChange('');
                        break;
                    case 38: // up
                        event.preventDefault();
                        if (open) {
                            const index = selected <= 0 ? suggestions.length - 1 : selected - 1;
                            setSelected(index);
                            scrollToItem(listRef.current, listRef.current.children[index]);
                        }
                        break;
                    case 40: // down
                        event.preventDefault();
                        if (open) {
                            const index =
                                selected === -1 || selected === suggestions.length - 1
                                    ? 0
                                    : selected + 1;
                            setSelected(index);
                            scrollToItem(listRef.current, listRef.current.children[index]);
                        }
                        break;
                }
            },
            [
                debouncedChange,
                hideList,
                onTextChange,
                open,
                selectSuggestion,
                selected,
                suggestions.length,
            ],
        );

        const handleChange = useCallback(
            (event) => debouncedChange(event.target.value),
            [debouncedChange],
        );

        const handleFocus = useCallback(() => {
            if (suggestions.length !== 0) {
                setOpen(true);
                setSelected(autoSelect ? 0 : -1);
            }
        }, [suggestions, autoSelect]);

        const handleBlur = useCallback(() => {
            setOpen(false);
            if (!tag) onTextChange('');
        }, [tag]);

        const handleAddClick = useCallback(() => {
            const input = document.getElementById(id);
            input.focus();
            debouncedChange.flush();
        }, [debouncedChange, id]);

        const handleListMouseDown = useCallback((event) => event.preventDefault(), []);

        const handleListMouseUp = useCallback(
            (event) => {
                const element = event.target.closest('[role=option]');
                if (element) {
                    event.preventDefault();
                    selectSuggestion(+element.dataset.index);
                }
            },
            [selectSuggestion],
        );

        useEffect(() => {
            if (!text) setOpen(false);

            if (error || text[0] === '/') {
                hideList();
                updateSuggestions.cancel();
            } else {
                if (text && mounted.current) {
                    updateSuggestions(text);
                } else {
                    Promise.resolve(getSuggestions(text || '')).then((suggestions) => {
                        setSuggestions(suggestions);
                    }),
                        (mounted.current = true);
                }
            }
            return updateSuggestions.cancel;
        }, [hideList, updateSuggestions, text, error]);

        useEffect(() => {
            const button = buttonRef.current;
            const { bottom, left, width } = button.getBoundingClientRect();

            const list = listRef.current;
            list.style.top = `${bottom}px`;
            list.style.left = `${left}px`;
            list.style.width = `${width}px`;
            list.dataset.layer = button.dataset.layer;
            if (open) {
                list.style.display = 'block';
            } else {
                list.style.display = 'none';
            }
        }, [open]);

        const listId = `${id}-list`;
        return (
            <Layer className='ComboBox' ref={buttonRef}>
                {typeof tag.value === 'object' && (
                    <div className='ComboBox__prefixIcon'>
                        <Icon type={tag.value.type} size='medium' />
                    </div>
                )}
                <input
                    {...props}
                    id={id}
                    ref={ref}
                    className={`ComboBox__input${error ? ' ComboBox--error' : ''}${
                        typeof tag.value === 'object' ? ' ComboBox__input--hasPrefixIcon' : ''
                    }`}
                    autoComplete='off'
                    role='combobox'
                    aria-expanded={open}
                    aria-autocomplete='list'
                    aria-controls={listId}
                    aria-activedescendant={selected === -1 ? null : `${id}-${selected}`}
                    value={text}
                    onKeyDown={handleKeyDown}
                    onChange={handleChange}
                    onFocus={handleFocus}
                    onBlur={handleBlur}
                />
                {!autoSelect && (
                    <IconButton
                        id={`${id}-add`}
                        className='ComboBox__add'
                        icon={faPlus}
                        aria-label={t`Add`}
                        disabled={!text}
                        onClick={handleAddClick}
                    />
                )}
                {createPortal(
                    <div
                        id={listId}
                        className='ComboBox__list'
                        role='listbox'
                        aria-label={`Options`}
                        style={{ display: 'none' }}
                        ref={listRef}
                        onMouseDown={handleListMouseDown}
                        onMouseUp={handleListMouseUp}>
                        {suggestions.map((item, index) => {
                            const element = renderSuggestion(item, index);
                            return cloneElement(element, {
                                key: index,
                                id: `${id}-${index}`,
                                role: 'option',
                                className: `ComboBox__option ${element.props.className}`,
                                'aria-selected': selected === index,
                                'data-index': index,
                            });
                        })}
                    </div>,
                    document.body,
                )}
            </Layer>
        );
    },
);

export default ComboBox;
