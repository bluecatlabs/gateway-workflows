import React from 'react';
import {
    faCube,
    faNetworkWired,
    faGlobe,
    faShield,
    faServer,
    faObjectGroup,
    faEthernet,
} from '@fortawesome/free-solid-svg-icons';
import { IconButton } from '@bluecateng/pelagos';
import './Icon.less';

function Icon(props) {
    const { type, size } = props;

    switch (type) {
        case 'IPv4Block':
        case 'IPv6Block':
        case 'Block':
            return <IconButton icon={faCube} className='PrefixIcon' type='ghost' size={size} />;
        case 'IPv4Network':
        case 'IPv6Network':
        case 'Network':
            return (
                <IconButton icon={faNetworkWired} className='PrefixIcon' type='ghost' size={size} />
            );
        case 'View':
            return <IconButton icon={faGlobe} className='PrefixIcon' type='ghost' size={size} />;
        case 'Zone':
            return <IconButton icon={faShield} className='PrefixIcon' type='ghost' size={size} />;
        case 'Server':
            return <IconButton icon={faServer} className='PrefixIcon' type='ghost' size={size} />;
        case 'Interface':
            return <IconButton icon={faEthernet} className='PrefixIcon' type='ghost' size={size} />;
        case 'ServerGroup':
            return (
                <IconButton icon={faObjectGroup} className='PrefixIcon' type='ghost' size={size} />
            );
        default:
            return <></>;
    }
}

export default Icon;
