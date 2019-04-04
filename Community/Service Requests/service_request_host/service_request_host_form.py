"""
Add host record form
"""
from bluecat.wtform_fields import IP4Address, CustomStringField, CustomBooleanField, PlainHTML, CustomSearchButtonField, CustomSubmitField
from bluecat.wtform_extensions import GatewayForm
from .service_request_host_wtform_fields import CustomZone, IP4Network, CustomIP4Address
from .service_request_host_endpoints import get_next_ip4_address_endpoint


def filter_reserved(res):
    """
    Filter reserved IP.

    :param res:
    :return:
    """
    try:
        if res['data']['state'] == 'RESERVED':
            res['status'] = 'FAIL'
            res['message'] = 'Host records cannot be added if ip address is reserved.'
        return res
    except (TypeError, KeyError):
        return res


class GenericFormTemplate(GatewayForm):
    """ Form to generate HTML and Javascript for the snow_add_host_record_example workflow

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'service_request_host'
    workflow_permission = 'service_request_host_page'

    zone = CustomZone(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Zone',
        required=True,
        is_disabled_on_start=False
    )

    input_x1_button_x1_aligned_open_1 = PlainHTML('<div class="input_x1_button_x1_aligned">')

    input_x1_aligned_open_1 = PlainHTML('<div class="input_x1_aligned">')

    ip4_network = IP4Network(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Network (Optional)',
        required=False,
        one_off=False,
        is_disabled_on_start=False
    )

    input_x1_aligned_close_1 = PlainHTML('</div>')

    get_next_available_ip4 = CustomSearchButtonField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Get Next IPv4',
        server_side_method=get_next_ip4_address_endpoint,
        on_complete=['populate_ip4_address'],
        is_disabled_on_start=False,
    )

    input_x1_button_x1_aligned_close_1 = PlainHTML('</div>')

    clearfix_2 = PlainHTML('<div class="clearfix"> </div>')

    ip4_address = CustomIP4Address(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='IP Address',
        required=True,
        inputs={'address': 'ip4_address'},
        result_decorator=filter_reserved,
        should_cascade_disable_on_change=True,
        is_disabled_on_start=False
    )

    hostname = CustomStringField(
        label='Hostname',
        required=True,
        is_disabled_on_start=False
    )

    deploy_now = CustomBooleanField(
        label='Deploy Now',
        is_disabled_on_start=False
    )

    submit = CustomSubmitField(
        label='Submit',
        is_disabled_on_start=False
    )
