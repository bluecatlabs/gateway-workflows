const getLiveElement = () => {
    let element = document.getElementById('liveText');
    if (!element) {
        element = document.createElement('div');
        element.id = 'liveText';
        element.className = 'assistive-text';
        element.setAttribute('aria-live', 'assertive');
        document.body.appendChild(element);
    }
    return element;
};

/**
 * Sets the specified text on an element marked as `aria-live="assertive"`.
 * The element is created as required and reused in subsequent calls.
 * @param {string} text the text.
 *
 * @example
 * import {useCallback} from 'react';
 * import {setLiveText} from '@bluecateng/pelagos';
 *
 * const Example = () => {
 *   const handleClick = useCallback(() => setLiveText('Example text'), []);
 *   return <button onClick={handleClick}>...</button>;
 * }
 */
const setLiveText = (text) => (getLiveElement().textContent = text);

export default setLiveText;
