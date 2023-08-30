import { ACTION_NAMES } from '../constants/action';

const checkDestinationFill = ({ destination, selectedAction }) => {
    switch (selectedAction?.name) {
        case ACTION_NAMES.COPY_ROLES_TO_SERVER:
        case ACTION_NAMES.MOVE_ROLES_TO_SERVER:
        case ACTION_NAMES.MOVE_PRIMARY_ROLE:
            if (destination.serverInterface.interface.ip != null) return true;
        case ACTION_NAMES.COPY_ROLES_TO_ZONES:
            return destination.zoneList.length > 0 || destination.reverseZoneList.length > 0;
        case ACTION_NAMES.ADD_SERVERS:
            return (
                (destination.serverInterfaceList.length > 0 ||
                    (destination.candidateServer.value &&
                        destination.candidateSvInterface?.name &&
                        destination.candidateSvInterface?.name !== 'Select Interface')) &&
                destination.roleType &&
                !destination.serverInterfaceList
                    .map((s) => s.serverInterface)
                    .includes(destination.zoneTransferInterface)
            );
    }
};

export { checkDestinationFill };
