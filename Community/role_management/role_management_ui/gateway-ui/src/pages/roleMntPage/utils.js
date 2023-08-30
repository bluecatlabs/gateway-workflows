import { FILTER_OPTIONS } from './constants/filter';

const getOptions = ({ fieldName, prefix }) => {
    const allOptions = FILTER_OPTIONS[fieldName];
    let selected = [];
    return new Promise((resolve, reject) => {
        if (prefix && allOptions)
            selected = allOptions.filter((o) => o.label.startsWith(prefix)).slice(0, 10);
        setTimeout(() => resolve(selected), 400);
    });
};

export { getOptions };
