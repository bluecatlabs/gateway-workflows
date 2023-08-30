export default (...refs) =>
    (current) => {
        for (const ref of refs) {
            if (typeof ref === 'function') {
                ref(current);
            } else {
                ref.current = current;
            }
        }
    };
