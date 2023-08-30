import './SelectArrow.less';

export const SelectArrow = ({ className }) => (
    <svg className={`SelectArrow ${className}`} viewBox='0 0 16 16' aria-hidden='true'>
        <path d='M8 11L3 6 3.7 5.3 8 9.6 12.3 5.3 13 6z' />
    </svg>
);

export default SelectArrow;
