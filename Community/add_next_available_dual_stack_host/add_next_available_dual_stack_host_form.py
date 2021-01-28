# Copyright 2020 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
import datetime

from wtforms import StringField, PasswordField, FileField
from wtforms import BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, MacAddress, URL
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, Zone, View, PlainHTML, CustomBooleanField
from .add_next_available_dual_stack_host_wtform_fields import IP4Network, IP6Network


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'add_next_available_dual_stack_host'
    workflow_permission = 'add_next_available_dual_stack_host_page'
    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Configuration',
        required=True,
        coerce=int,
        validators=[],
        is_disabled_on_start=False,
        on_complete=['call_view'],
        enable_on_complete=['view'],
        clear_below_on_change=False
    )

    view = View(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='View',
        required=True,
        one_off=True,
        on_complete=['call_zone'],
        clear_below_on_change=False,
        enable_dependencies={'on_complete': ['zone']},
        disable_dependencies={'on_change': ['zone']},
        clear_dependencies={'on_change': ['zone']},
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True
    )

    zone = Zone(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Zone',
        required=True,
        clear_below_on_change=False,
        enable_dependencies={'on_complete': ['hostname', 'ip4_network', 'ip6_network']},
        disable_dependencies={'on_change': ['hostname', 'ip4_network', 'ip6_network']},
        clear_dependencies={'on_change': ['hostname', 'ip4_network', 'ip6_network']},
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True
    )

    hostname = CustomStringField(
        label='Hostname',
        required=True
    )

    ip4_network = IP4Network(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='IPv4 Network',
        required=True,
        one_off=False,
        is_disabled_on_start=False
    )

    ip6_network = IP6Network(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='IPv6 Network',
        required=True,
        one_off=False,
        enable_dependencies={'on_complete': ['submit']},
        disable_dependencies={'on_change': ['submit']},
        is_disabled_on_start=False
    )

    add_device = CustomBooleanField(
        label='Add Device',
        is_disabled_on_start=False
    )

    submit = SubmitField(label='Submit')

    # Button with JS to clear the form
    clear_button = PlainHTML('<button type="button" onclick="clearForm();" class="clearForm">Clear Form</button>')
