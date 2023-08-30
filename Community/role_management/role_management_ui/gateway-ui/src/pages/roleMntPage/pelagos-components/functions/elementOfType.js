/** Ensures an instance of a specific component is passed.
 * Adapted from: https://github.com/facebook/react/issues/2979#issuecomment-789320781
 *
 * @param {function|string} type The expected component type.
 * @returns {function}
 * @private
 */
export default (type) => {
    if (process.env.NODE_ENV === 'production') {
        return () => null;
    }

    const expectedName = type.displayName || type.name || type;
    const validate = (props, propName, componentName, location, propFullName) => {
        const prop = props[propName];
        const actualType = prop.type;
        return actualType === type
            ? null
            : new Error(
                  `Invalid ${location} \`${propFullName || propName}\` of type \`${
                      actualType?.displayName || actualType?.name || actualType || typeof prop
                  }\` supplied to \`${componentName}\`, expected instance of \`${expectedName}\`.`,
              );
    };
    const checkOptional = (props, propName, componentName, location, propFullName) =>
        props[propName] ? validate(props, propName, componentName, location, propFullName) : null;
    checkOptional.isRequired = (props, propName, componentName, location, propFullName) => {
        const prop = props[propName];
        return prop
            ? validate(props, propName, componentName, location, propFullName)
            : new Error(
                  `The ${location} \`${
                      propFullName || propName
                  }\` is marked as required in \`${componentName}\`, but its value is \`${
                      prop === null ? 'null' : 'undefined'
                  }\`.`,
              );
    };
    return checkOptional;
};
