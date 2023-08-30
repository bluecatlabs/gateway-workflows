function sameMembers(arr1, arr2) {
    const set1 = new Set(arr1);
    const set2 = new Set(arr2);
    return arr1.every((item) => set2.has(item)) && arr2.every((item) => set1.has(item));
}

/**
 * Compare two strings
 * @param string1 string passed by the user
 * @param string2 string passed by the user
 * @returns {number}
 */

const collator = new Intl.Collator();
function stringCompare(string1, string2) {
    return collator.compare((string1 || '').toLowerCase(), (string2 || '').toLowerCase());
}

export { sameMembers, stringCompare };
