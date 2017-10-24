# Copyright 2017 BlueCat Networks. All rights reserved.

from wtforms import SubmitField
from bluecat.wtform_fields import Configuration, View, Zone, CustomStringField
from bluecat.wtform_extensions import GatewayForm


class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'add_text_record_example'
    workflow_permission = 'add_text_record_example_page'
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
        enable_on_complete=['name', 'text', 'submit']
    )

    name = CustomStringField(
        label='Name'
    )

    text = CustomStringField(
        label='Text'
    )

    submit = SubmitField(label='Submit')
