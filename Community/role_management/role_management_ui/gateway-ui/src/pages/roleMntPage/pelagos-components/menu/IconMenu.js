import {
    Children,
    cloneElement,
    forwardRef,
    useCallback,
    useLayoutEffect,
    useMemo,
    useRef,
    useState,
} from 'react';
import { createPortal } from 'react-dom';

import setRefs from '../functions/setRefs';
import useRandomId from '../hooks/useRandomId';
import IconButton from './IconButton';
import './IconMenu.less';
import Layer from './Layer';

const checkEnabled = (index, increment, children) => {
    const last = children.length - 1;
    do {
        index += increment;
        if (index < 0) {
            index = last;
        } else if (index > last) {
            index = 0;
        }
    } while (children[index].props.disabled);
    return index;
};

/** An icon button with a pop-up menu. */
const IconMenu = forwardRef(
    ({ id, className, icon, disabled, flipped, children, ...props }, ref) => {
        id = useRandomId(id);
        const menuId = `${id}-menu`;
        const buttonRef = useRef(null);
        const menuRef = useRef(null);
        const [current, setCurrent] = useState(-1);

        const menuVisible = current !== -1;

        const childArray = useMemo(() => Children.toArray(children), [children]);
        const allDisabled = useMemo(
            () => childArray.every((child) => child.props.disabled),
            [childArray],
        );

        const handleButtonClick = useCallback(
            () => setCurrent((current) => (current === -1 ? checkEnabled(-1, 1, childArray) : -1)),
            [childArray],
        );

        const handleButtonKeyDown = useCallback(
            (event) => {
                if (
                    menuVisible &&
                    !event.shiftKey &&
                    !event.ctrlKey &&
                    !event.altKey &&
                    !event.metaKey
                ) {
                    const keyCode = event.keyCode;
                    switch (keyCode) {
                        case 13: // enter
                        case 32: // space
                            event.preventDefault();
                            setCurrent(
                                (current) => (menuRef.current.childNodes[current].click(), -1),
                            );
                            break;
                        case 27: // escape
                            event.preventDefault();
                            setCurrent(-1);
                            break;
                        case 35: // end
                            event.preventDefault();
                            setCurrent(checkEnabled(childArray.length, -1, childArray));
                            break;
                        case 36: // home
                            event.preventDefault();
                            setCurrent(checkEnabled(-1, 1, childArray));
                            break;
                        case 38: // up
                            event.preventDefault();
                            setCurrent((current) => checkEnabled(current, -1, childArray));
                            break;
                        case 40: // down
                            event.preventDefault();
                            setCurrent((current) => checkEnabled(current, 1, childArray));
                            break;
                    }
                }
            },

            [childArray, menuVisible],
        );

        const handleButtonBlur = useCallback(() => setCurrent(-1), []);

        const handleMenuMouseDown = useCallback((event) => event.preventDefault(), []);

        const handleMenuMouseUp = useCallback(
            (event) => {
                const element = event.target.closest('li');
                if (element) {
                    event.preventDefault();
                    const item = childArray[+element.dataset.index];
                    if (!item.props.disabled) {
                        element.click();
                        setCurrent(-1);
                    }
                }
            },
            [childArray],
        );

        useLayoutEffect(() => {
            if (menuVisible) {
                const button = buttonRef.current;
                const { bottom, left, right } = button.getBoundingClientRect();

                const menu = menuRef.current;
                menu.style.top = `${bottom}px`;
                menu.style.left = flipped ? `${right - menu.offsetWidth}px` : `${left}px`;
                menu.dataset.layer = button.parentNode.dataset.layer;
            }
        }, [menuVisible, flipped]);

        return (
            <Layer>
                <IconButton
                    {...props}
                    id={id}
                    className={`IconMenu${className ? ` ${className}` : ''}`}
                    icon={icon}
                    disabled={disabled || allDisabled}
                    aria-controls={menuVisible ? menuId : null}
                    aria-haspopup='true'
                    aria-expanded={menuVisible}
                    aria-activedescendant={menuVisible ? `${id}-${current}` : null}
                    ref={ref ? setRefs(ref, buttonRef) : buttonRef}
                    onClick={handleButtonClick}
                    onKeyDown={handleButtonKeyDown}
                    onBlur={handleButtonBlur}
                />
                {menuVisible &&
                    createPortal(
                        <ul
                            id={menuId}
                            className='IconMenu__menu'
                            role='menu'
                            ref={menuRef}
                            onMouseDown={handleMenuMouseDown}
                            onMouseUp={handleMenuMouseUp}>
                            {Children.map(children, (child, index) =>
                                cloneElement(child, {
                                    id: `${id}-${index}`,
                                    className: `${child.props.className || ''}${
                                        index === current ? ' IconMenu--current' : ''
                                    }`,
                                    'data-index': index,
                                }),
                            )}
                        </ul>,
                        document.body,
                    )}
            </Layer>
        );
    },
);

export default IconMenu;
