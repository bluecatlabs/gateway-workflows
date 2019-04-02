from flask import g, flash

from bluecat.api_exception import PortalException
import config.default_config as config
from bluecat.util import safe_str


def get_acls(**kwargs):
    """
    Retrieve all ACLs from default configuration
    :return: All ACLs in default configuration
    """
    # Use the default result template to store results
    result = []

    # Retrieve the configuration object
    try:
        configuration = g.user.get_api().get_configuration(config.default_configuration)
    except PortalException as e:
        g.user.logger.error('%s' % e, msg_type=g.user.logger.EXCEPTION)
        flash('Configuration %s could not be retrieved from the Gateway configuration' % config.default_configuration)
        return result

    # Retrieve list of ACLs from configuration
    acls = configuration.get_children_of_type('ACL')

    # Loop through ACLs appending to result dictionary
    for acl in acls:
        result.append((acl.get_id(), safe_str(acl.get_name())))

    return result
