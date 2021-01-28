# Copyright 2020 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
import datetime

from wtforms import StringField, PasswordField, FileField
from wtforms import BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, MacAddress, URL
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, IP4Address, View, Zone, CustomBooleanField, \
    PlainHTML
from .add_dual_stack_host_wtform_fields import IP6Address


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
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'add_dual_stack_host'
    workflow_permission = 'add_dual_stack_host_page'
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
        enable_dependencies={'on_complete': ['hostname', 'ip_address', 'ip6_address']},
        disable_dependencies={'on_change': ['hostname', 'ip_address', 'ip6_address']},
        clear_dependencies={'on_change': ['hostname', 'ip_address', 'ip6_address']},
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True
    )

    hostname = CustomStringField(
        label='Hostname',
        required=True
    )

    ip_address = IP4Address(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='IPv4 Address',
        required=True,
        inputs={'configuration': 'configuration', 'address': 'ip_address'},
        result_decorator=filter_reserved,
        enable_dependencies={'on_complete': ['submit', 'ip6_address']},
        disable_dependencies={'on_change': ['submit', 'ip6_address']},
        should_cascade_disable_on_change=True
    )

    ip6_address = IP6Address(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='IPv6 Address',
        required=True,
        inputs={'configuration': 'configuration', 'ip6_address': 'ip6_address'},
        result_decorator=None,
        disable_dependencies={'on_change': ['hostname', 'submit', 'ip_address']},
        enable_on_complete=['submit']
    )

    add_device = CustomBooleanField(
        label='Add Device',
        is_disabled_on_start=False
    )

    submit = SubmitField(label='Submit')

    # Button with JS to clear the form
    clear_button = PlainHTML('<button type="button" onclick="clearForm();" class="clearForm">Clear Form</button>')
