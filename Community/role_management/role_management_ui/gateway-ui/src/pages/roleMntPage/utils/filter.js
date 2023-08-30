export const formatFilterItems = (filters) => {
    const newFilters = { ...filters };
    for (const k of Object.keys(filters)) {
        if (filters[k]?.length === 0 || !Array.isArray(filters[k])) {
            delete newFilters[k];
        } else {
            newFilters[k] = newFilters[k].map((o) =>
                o.serverInterface
                    ? { label: o.serverInterface.name, value: o.serverInterface.name }
                    : o,
            );
        }
    }
    return newFilters;
};
