# Copyright 2017 BlueCat Networks. All rights reserved.

from wtforms import SubmitField
from bluecat.wtform_fields import Configuration, View, Zone, IP4Address, CustomStringField
from bluecat.wtform_extensions import GatewayForm


def filter_unallocated(res):
    if res['status'] == 'SUCCESS' and res['data']['state'] != u'UNALLOCATED':
        res['status'] = 'FAIL'
        res['message'] = 'IP status must be unallocated.'
    return res


class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'add_static_ip4_address_example'
    workflow_permission = 'add_static_ip4_address_example_page'
    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Configuration',
        required=True,
        coerce=int,
        validators=[],
        is_disabled_on_start=False,
        enable_on_complete=['ip4_address'],
    )

    ip4_address = IP4Address(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Address',
        required=True,
        inputs={'configuration': 'configuration', 'address': 'ip4_address'},
        result_decorator=filter_unallocated,
        on_complete=['call_view'],
        enable_on_complete=['view', 'mac_address', 'description', 'submit']
    )

    mac_address = CustomStringField(
        label='MAC Address'
    )

    description = CustomStringField(
        label='Description'
    )

    view = View(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='View',
        one_off=True,
        on_complete=['call_zone'],
        on_change=['view_changed'],
        clear_below_on_change=False,
        enable_on_complete=['zone']
    )

    zone = Zone(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Zone',
        on_change=['reset_hostname'],
        clear_below_on_change=False,
        enable_on_complete=['hostname']
    )

    hostname = CustomStringField(
        label='Hostname'
    )

    submit = SubmitField(label='Submit')
