import './Tooltip.less';
import { useCallback, useMemo, useRef } from 'react';

const { round } = Math;

const arrowSpacing = 9;

const getOffset = (position, size, windowSize) =>
    position < 0 ? -position : position + size > windowSize ? windowSize - position - size : 0;

const updatePosition = (target, tooltip, placement) => {
    const { left, top, width, height } = target.getBoundingClientRect();
    const { width: childWidth, height: childHeight } = tooltip.getBoundingClientRect();

    let tooltipLeft, tooltipTop, arrowPosition;
    if (placement === 'left' || placement === 'right') {
        tooltipTop = top + (height - childHeight) / 2;
        tooltipLeft =
            left + (placement === 'left' ? -childWidth - arrowSpacing : width + arrowSpacing);
        const offset = getOffset(tooltipTop, childHeight, window.innerHeight);
        tooltipTop += offset;
        arrowPosition = 50 * (1 - (2 * offset) / childHeight) + '%';
    } else {
        tooltipLeft = left + (width - childWidth) / 2;
        tooltipTop =
            top + (placement === 'top' ? -childHeight - arrowSpacing : height + arrowSpacing);
        const offset = getOffset(tooltipLeft, childWidth, window.innerWidth);
        tooltipLeft += offset;
        arrowPosition = 50 * (1 - (2 * offset) / childWidth) + '%';
    }

    tooltip.style.left = `${round(tooltipLeft)}px`;
    tooltip.style.top = `${round(tooltipTop)}px`;
    tooltip.style.setProperty('--arrow-position', arrowPosition);
};

const createTooltip = () => {
    const tooltip = document.createElement('div');
    tooltip.id = `tooltip-${('' + Math.random()).slice(2)}`;

    const animation = tooltip.animate([{ opacity: 0 }, { opacity: 1 }], {
        duration: 150,
        fill: 'both',
        easing: 'ease-out',
    });
    animation.onfinish = ({ currentTime }) => {
        if (currentTime === 0 && tooltip.parentNode) {
            document.body.removeChild(tooltip);
        }
    };
    animation.pause();

    return [tooltip, animation];
};

/**
 * return type for `useTooltipBase`.
 * @typedef {Array} useTooltipBase~Return
 * @property {function(string, string, Element): void} 0 function to show tooltip.
 * @property {function(): void} 1 function to hide tooltip.
 */

/**
 * Returns a tuple with two functions to show and hide a tooltip.
 * @returns {useTooltipBase~Return} tuple with show and hide functions.
 *
 * @example
 * import {useCallback, useRef} from 'react';
 * import {useTooltipBase} from '@bluecateng/pelagos';
 *
 * const Example = () => {
 *   const [show, hide] = useTooltipBase();
 *   const ref = useRef(null);
 *   const handleClick = useCallback(() => show('Example tooltip', 'top', ref.current), [show]);
 *   return (
 *     <div ref={ref}>
 *       <button onClick={handleClick}>Show</button>
 *       <button onClick={hide}>Hide</button>
 *     </div>
 *   )
 * }
 */
const useTooltipBase = () => {
    const targetRef = useRef(null);
    const [tooltip, animation] = useMemo(() => createTooltip(), []);
    const show = useCallback(
        (text, placement, target) => {
            if (text) {
                tooltip.className = `Tooltip Tooltip--${placement}`;
                tooltip.textContent = text;
                document.body.appendChild(tooltip);
                animation.pause();
                animation.playbackRate = 1;
                animation.play();

                target.setAttribute('aria-describedby', tooltip.id);
                updatePosition(target, tooltip, placement);
                targetRef.current = target;
            }
        },
        [tooltip, animation],
    );
    const hide = useCallback(() => {
        if (tooltip.parentNode) {
            targetRef.current.removeAttribute('aria-describedby');
            animation.pause();
            animation.playbackRate = -1;
            animation.play();
        }
    }, [tooltip, animation]);
    return [show, hide];
};

export default useTooltipBase;
