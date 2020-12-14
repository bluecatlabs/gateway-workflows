# Copyright 2019 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
import datetime

from wtforms import SelectField, TextAreaField
from wtforms import BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, MacAddress, URL
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, View, PlainHTML


class GenericFormTemplate(GatewayForm):

    workflow_name = 'bulk_engine_example'
    workflow_permission = 'bulk_engine_example_page'

    results = PlainHTML()

    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Configuration',
        required=True,
        coerce=int,
        validators=[],
        is_disabled_on_start=False,
        on_complete=['call_view'],
        enable_dependencies={'on_complete': ['view']},
        disable_dependencies={'on_change': ['view']},
        clear_dependencies={'on_change': ['view']},
        clear_below_on_change=False
    )

    view = View(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='View',
        required=True,
        one_off=True,
        clear_below_on_change=False,
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True,
        enable_dependencies={'on_complete': ['on_fail', 'data_box', 'submit']}
    )

    on_fail = SelectField(
        label='On Fail',
        choices=(('skip', 'Skip'), ('abort', 'Abort'))
    )

    data_box = TextAreaField(
        label='Data',
        default="""{
        "networks":[
            {"action":"ADD", "address":"51.0.8.0", "cidr":"24"},
            {"action":"ADD", "address": "51.0.6.0", "cidr": "27", "name":"my_Other_net"},
            {"action":"ADD", "address": "52.0.0.0", "cidr": "24", "name":"my_net"},
            {"action":"ADD", "address": "51.0.0.0", "cidr": "16"}
        ],
        "ip_addresses":[
            {"action": "ADD", "address": "51.0.8.5"},
            {"action": "ADD", "address": "51.0.8.17"},
            {"action": "ADD", "address": "51.0.85.5"}
        ],
        "dns_records":[
            {"action": "ADD", "type":"A", "address": "51.0.8.6", "record": "abc", "zone":"example.com"},
            {"action": "ADD", "type": "C", "linked_fqdn": "abc.example.com", "record": "yyz", "zone": "example.com"}
        ]
    }"""
    )

    submit = SubmitField(label='Submit')
