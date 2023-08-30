import smoothScroll from './smoothScroll';

const { floor, min } = Math;

export default (element, current) => {
    const listHeight = element.clientHeight;
    const scrollTop = element.scrollTop;
    const scrollMax = element.scrollHeight - listHeight;
    const children = element.children;
    const lastIndex = children.length - 1;
    if (scrollTop >= scrollMax) {
        return lastIndex;
    }

    const optionHeight = children[0].offsetHeight;
    const count = floor(listHeight / optionHeight);
    const offset = min(optionHeight * count, scrollMax - scrollTop);
    smoothScroll(element, scrollTop, offset, 150);
    return min(lastIndex, current + count);
};
