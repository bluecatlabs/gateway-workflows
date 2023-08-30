const optionsToParamValue = (options) => options.map((o) => o.label).join(',');

const roleOptionsToParamValue = (options) => options.map((o) => o.value).join(',');

export { optionsToParamValue, roleOptionsToParamValue };
