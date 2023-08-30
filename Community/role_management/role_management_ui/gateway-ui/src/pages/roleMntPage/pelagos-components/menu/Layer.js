import { createContext, forwardRef, useContext } from 'react';

const { min } = Math;

export const LayerContext = createContext(0);

/** Starts a new layer. */
const Layer = forwardRef(({ as: BaseComponent = 'div', children, ...props }, ref) => {
    const layer = min(useContext(LayerContext) + 1, 3);
    return (
        <LayerContext.Provider value={layer}>
            <BaseComponent {...props} data-layer={layer} ref={ref}>
                {children}
            </BaseComponent>
        </LayerContext.Provider>
    );
});

export default Layer;
