import os
import sys

from flask import g, request, jsonify

from bluecat import route, util
from bluecat.api_exception import PortalException
from bluecat.util import rest_exception_catcher, rest_workflow_permission_required
from bluecat.wtform_fields import SimpleAutocompleteField
import config.default_config as config
from main_app import app


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


SUCCESS = 'SUCCESS'
FAIL = 'FAIL'


def get_result_template():
    return {'status': FAIL, 'message': '', 'data': {}}


def empty_decorator(res):
    """
    Default 'do nothing' decorator applied to every result set.
    """
    return res


class Location(SimpleAutocompleteField):
    """
    Autocomplete enabled field for Location entities.

    :param label: HTML label for the generated field.
    :param validators: WTForm validators for the field run on the server side.
    :param kwargs: Other keyword arguments for WTForms Fields.

    """
    def __init__(self, label='Location', validators=None, result_decorator=None, **kwargs):
        """ Pass parameters to SimpleAutocompleteField for initialization.
        """
        super(Location, self).__init__(
            label,
            validators,
            server_side_method=get_locations_endpoint,
            result_decorator=result_decorator,
            **kwargs)


def get_locations_endpoint(workflow_name, element_id, permissions, result_decorator=None):
    endpoint = 'get_locations'
    function_endpoint = '%sget_locations' % workflow_name
    view_function = app.view_functions.get(function_endpoint)
    if view_function is not None:
        return endpoint

    if not result_decorator:
        result_decorator = empty_decorator

    @route(app, '/%s/%s' % (workflow_name, endpoint), methods=['POST'])
    @rest_workflow_permission_required(permissions)
    @rest_exception_catcher
    # pylint: disable=unused-variable
    def get_locations():
        """
        Exposed endpoint for retrieving zones with a given hint in a view. Used for populating select fields, does not
        return all information.
        """
        hint = request.form['parent_location']
        return jsonify(result_decorator(get_locations_by_hint(hint)))

    return endpoint


def get_locations_by_hint(hint):
    """
    Get a list of zone FQDNs that corresponds to the given configuration, view and hint.

    :param configuration_id: The ID of the configuration in which the zone resides.
    :param view_name: The name of the view in which the zone resides.
    :param hint: Partial or full name of zone to find.
    :return: FQDN of any zones that match the given hint as data in JSON, using result template format.
    """
    result = {'status': FAIL, 'message': '', 'data': {}}
    try:
        result['status'] = SUCCESS
        result['data']['autocomplete_field'] = []
        result['data']['select_field'] = []
        if hint != '':
            foundlocations = g.user.get_api().get_by_object_types(hint, 'Location')
            count = 0
            for location in foundlocations:
                location_name = '%s (%s)' % (location.get_name(), location.get_property('code'))
                result['data']['autocomplete_field'].append({
                    'input': location.get_property('code'),
                    'value': location_name
                })
                result['data']['select_field'].append({
                    'id': location.get_property('code'),
                    'txt': location_name
                })

                if count == 10:
                    break
                count += 1
    except PortalException as e:
        result['status'] = FAIL
        result['message'] = 'Error while searching for Locations: %s and hint: %s!' % (util.safe_str(e), hint)

    return result