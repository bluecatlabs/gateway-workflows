# Copyright 2017 BlueCat Networks. All rights reserved.

from wtforms import SubmitField
from bluecat.wtform_fields import Configuration, View, Zone, HostRecord, CustomStringField, PlainHTML
from bluecat.wtform_fields import get_host_records_endpoint
from bluecat.wtform_extensions import GatewayForm


class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'delete_host_record_example'
    workflow_permission = 'delete_host_record_example_page'
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
        on_complete=[],
        enable_on_complete=['parent_zone'],
    )

    parent_zone = Zone(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Zone',
        required=True,
        start_initialized=True,
        inputs={'zone': 'parent_zone', 'configuration': 'configuration', 'view': 'view'},
        enable_on_complete=['host_record']
    )

    host_record = HostRecord(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Host Record',
        required=True,
        inputs={
            'configuration': 'configuration',
            'view': 'view',
            'parent_zone': 'parent_zone',
            'host_record': 'host_record'
        },
        on_complete=['server_output_host_record'],
        server_outputs={'name': 'name', 'addresses': 'ip4_address'},
        server_side_output_method=get_host_records_endpoint,
        enable_on_complete=['submit', 'name', 'ip4_address']
    )

    seperator = PlainHTML('<hr>')

    name = CustomStringField(
        label='Name',
        readonly=True
    )

    ip4_address = CustomStringField(
        label='IP4 Address',
        readonly=True
    )

    submit = SubmitField(label='Delete')
