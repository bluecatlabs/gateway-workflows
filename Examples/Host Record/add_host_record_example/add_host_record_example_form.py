# Copyright 2017 BlueCat Networks. All rights reserved.

from wtforms import SubmitField
from bluecat.wtform_fields import Configuration, View, Zone, IP4Address, CustomStringField
from bluecat.wtform_extensions import GatewayForm


def filter_reserved(res):
    try:
        if res['data']['state'] == u'RESERVED':
            res['status'] = 'FAIL'
            res['message'] = 'Host records cannot be added if ip address is reserved.'
        return res
    except (TypeError, KeyError):
        return res


class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'add_host_record_example'
    workflow_permission = 'add_host_record_example_page'
    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Configuration',
        required=True,
        coerce=int,
        validators=[],
        is_disabled_on_start=False,
        on_complete=['call_view'],
        enable_on_complete=['view']
    )

    view = View(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='View',
        required=True,
        one_off=True,
        on_complete=['call_zone'],
        enable_on_complete=['zone']
    )

    zone = Zone(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Zone',
        required=True,
        enable_on_complete=['ip4_address']
    )

    ip4_address = IP4Address(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='IP Address',
        required=True,
        inputs={'configuration': 'configuration', 'address': 'ip4_address'},
        result_decorator=filter_reserved,
        enable_on_complete=['hostname', 'submit']
    )

    hostname = CustomStringField(
        label='Hostname',
        required=True
    )

    submit = SubmitField(label='Submit')
