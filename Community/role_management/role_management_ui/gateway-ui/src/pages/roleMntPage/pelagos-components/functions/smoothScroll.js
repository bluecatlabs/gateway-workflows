import animate from './animate';

/**
 * Scrolls the specified element using an animation.
 * @param {Element} element the element to scroll.
 * @param {number} initialTop the initial scroll top.
 * @param {number} offset the number of pixels to scroll.
 * @param {number} duration the duration of the animation.
 * @param {function(): void} [done] invoked after scrolling.
 * @returns {{cancel: (function(): void)}}
 *
 * @example
 * import {useCallback} from 'react';
 * import {smoothScroll} from '@bluecateng/pelagos';
 *
 * const Example = () => {
 *   const handleClick = useCallback(() => {
 *     const element = document.getElementById('other');
 *     smoothScroll(element, element.scrollTop, 100, 66);
 *   }, []);
 *   return <button onClick={handleClick}>...</button>;
 * }
 */
const smoothScroll = (element, initialTop, offset, duration, done) =>
    animate(
        duration,
        (current) => (element.scrollTop = initialTop + current * offset),
        () => {
            if (done) done();
            element.dispatchEvent(new CustomEvent('scroll'));
        },
    );

export default smoothScroll;
