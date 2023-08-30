import { Layer, SvgIcon } from '@bluecateng/pelagos';
import debounce from 'lodash-es/debounce';
import { cloneElement, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import Icon from '../components/icons/Icon';
import { compareObjects, listIncludesObj } from '../utils/common';
import scrollToItem from './functions/scrollToItem';
import setLiveText from './functions/setLiveText';
import useTooltip from './hooks/useTooltip';
import xmarkThin from './icons/xmarkThin';
import './TagInput.less';

const removeTag = (tags, i) => {
    const newTags = [...tags];
    newTags.splice(i, 1);
    return newTags;
};

const TagInput = (props) => {
    const {
        id,
        filterField,
        tags,
        defaultTags,
        defaultTooltipText,
        error,
        onChange,

        autoSelect,
        text,
        getSuggestions,
        renderSuggestion,
        onTextChange,
    } = props;

    const inputRef = useRef(null);
    const buttonRef = useRef(null);
    const listRef = useRef(null);
    const mounted = useRef(false);

    const tooltip = useTooltip(defaultTooltipText, 'top');

    const [suggestions, setSuggestions] = useState([]);
    const [open, setOpen] = useState(false);
    const [selected, setSelected] = useState(-1);

    const handleTagClick = useCallback(
        (event) => {
            const button = event.target.closest('button');
            if (button) {
                const index = +button.dataset.index;
                const name = tags[index].label;
                setLiveText(`${name} removed`);
                onChange(removeTag(tags, index));
                if (listRef.current.style.display !== 'none') {
                    inputRef.current.focus();
                }
            }
        },
        [tags, onChange],
    );

    const debouncedChange = useMemo(() => debounce(onTextChange, 33), [onTextChange]);

    const hideList = useCallback(() => (setSuggestions([]), setOpen(false), setSelected(-1)), []);

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
        (index) => {
            const selectedValue = suggestions[index];

            // ** tags ****
            if (
                listIncludesObj(
                    tags.map((tag) => tag.value),
                    selectedValue.value,
                )
            ) {
                const newTags = tags.filter((s) => !compareObjects(s.value, selectedValue.value));
                onChange(newTags);
            } else {
                onChange([...tags, selectedValue]);
            }
            onTextChange('');

            setOpen(false);
            inputRef.current.blur();
        },
        [suggestions, onTextChange],
    );

    const handleKeyDown = useCallback(
        (event) => {
            switch (event.keyCode) {
                // ***** remove tag *****
                case 8: // backspace
                    const value = event.target.value;
                    if (!value) {
                        event.preventDefault();
                        const length = tags.length;
                        if (length) {
                            const index = length - 1;
                            const name = tags[index].label;
                            setLiveText(`${name} removed`);
                            onChange(removeTag(tags, index));
                        }
                    }
                    break;
                case 13: // enter
                    event.preventDefault();
                    if (!text) return;
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

    const handleBlur = useCallback((event) => {}, []);

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
            if (mounted.current && text) updateSuggestions(text);
            else {
                Promise.resolve(getSuggestions('')).then((suggestions) => {
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
    }, [open, tags]);

    const handleClickOutside = useCallback(
        (event) => {
            if (
                !buttonRef.current.contains(event.target) &&
                !listRef.current.contains(event.target)
            ) {
                setOpen(false);
                onTextChange('');
            }
        },
        [buttonRef, listRef],
    );
    useEffect(() => {
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [buttonRef, listRef]);

    const listId = `${id}-list`;

    const length = tags.length;
    const renderTag = (tag) => {
        // if (tag.value.forwarderZone && !filterField) {
        //     return (
        //         <>
        //             <Icon type={'Zone'} size='small' />
        //             <span style={{ paddingRight: '6px' }}>{tag.label}</span>
        //             <span>{`(${tag.value.viewName})`}</span>
        //         </>
        //     );
        // }
        return (
            <>
                {typeof tag.value === 'object' && <Icon type={tag.value.type} size='small' />}
                <span>{tag.label}</span>
            </>
        );
    };

    return (
        <Layer
            id={`${id}-tags`}
            ref={buttonRef}
            className={`TagInput${error ? ' TagInput--error' : ''}`}
            onClick={handleTagClick}>
            {length
                ? tags.map((tag, i) => (
                      // can change key={tag.value}
                      <div key={tag.label} className='TagInput__tag'>
                          {renderTag(tag)}
                          <button
                              className='TagInput__remove'
                              type='button'
                              aria-label={`Remove ${tag.label}`}
                              data-index={i}>
                              <SvgIcon icon={xmarkThin} />
                          </button>
                      </div>
                  ))
                : defaultTags?.length
                ? defaultTags.map((tag) => (
                      <span key={tag.label} className='TagInput__defaultTag' ref={tooltip}>
                          {tag.label}
                      </span>
                  ))
                : null}

            <input
                {...props}
                id={id}
                ref={inputRef}
                className='TagInput__input'
                type='text'
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

            {createPortal(
                <div
                    id={listId}
                    className='TagInput__list'
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
                            className: `TagInput__option${
                                listIncludesObj(
                                    tags.map((tag) => tag.value),
                                    item.value,
                                )
                                    ? ` selected-tag`
                                    : ''
                            }`,
                            'aria-selected': selected === index,
                            'data-index': index,
                        });
                    })}
                </div>,
                document.body,
            )}
        </Layer>
    );
};

export default TagInput;
