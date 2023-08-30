import smoothScroll from './smoothScroll';

const { floor, max } = Math;

export default (element, current) => {
    const scrollTop = element.scrollTop;
    if (scrollTop === 0) {
        return 0;
    }

    const listHeight = element.clientHeight;
    const optionHeight = element.children[0].offsetHeight;
    const count = floor(listHeight / optionHeight);
    const offset = max(-optionHeight * count, -scrollTop);
    smoothScroll(element, scrollTop, offset, 150);
    return max(0, current - count);
};
