# Copyright 2017 BlueCat Networks. All rights reserved.

from wtforms import SubmitField
from bluecat.wtform_fields import Configuration, View, Zone, AliasRecord, CustomStringField
from bluecat.wtform_extensions import GatewayForm


class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'delete_alias_record_example'
    workflow_permission = 'delete_alias_record_example_page'
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
        enable_on_complete=['alias_record']
    )

    alias_record = AliasRecord(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Alias Record',
        required=True,
        on_complete=['populate_alias_record_data'],
        enable_on_complete=['name', 'linked_record', 'submit']
    )

    name = CustomStringField(
        label='Name',
        readonly=True
    )

    linked_record = CustomStringField(
        label='Linked Record',
        readonly=True
    )

    submit = SubmitField(label='Delete')
