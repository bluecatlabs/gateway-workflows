import './SelectArrow.less';

/** Arrow for select components. */
export const SelectArrow = ({ disabled }) => (
    <div className='ActionIcon'>
        <svg
            viewBox='0 0 16 16'
            aria-hidden='true'
            width='22px'
            className={`${disabled ? 'disabled' : 'primary'}`}>
            <path d='M8 11L3 6 3.7 5.3 8 9.6 12.3 5.3 13 6z' />
        </svg>
    </div>
);

export default SelectArrow;
