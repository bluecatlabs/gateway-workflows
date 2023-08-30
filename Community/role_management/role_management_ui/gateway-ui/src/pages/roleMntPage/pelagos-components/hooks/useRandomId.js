import { useMemo } from 'react';

/**
 * Returns either the specified string or a stable random string.
 * @param {string} [id] the ID to use.
 * @returns {string} the ID.
 * @private
 */
export default (id) => useMemo(() => id || `e${('' + Math.random()).slice(2)}`, [id]);
