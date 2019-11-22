# Copyright 2019 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
import datetime

from wtforms import StringField, PasswordField, FileField
from wtforms import BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, MacAddress, URL
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, Zone, View
from .create_server_vro_wtform_fields import IP4Network

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
    workflow_name = 'create_server_vro'
    workflow_permission = 'create_server_vro_page'
    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Configuration',
        required=True,
        coerce=int,
        clear_below_on_change=False,
        is_disabled_on_start=False,
        on_complete=['call_view'],
        enable_dependencies={'on_complete': ['view']},
        disable_dependencies={'on_change': ['view']},
        clear_dependencies={'on_change': ['view']}
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
        enable_dependencies={'on_complete': ['ip4_network']},
        disable_dependencies={'on_change': ['ip4_network']},
        clear_dependencies={'on_change': ['ip4_network']},
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True
    )

    ip4_network = IP4Network(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Network',
        required=True,
        one_off=False,
        enable_dependencies={'on_complete': ['mac_address', 'hostname', 'submit']},
        disable_dependencies={'on_change': ['mac_address', 'hostname', 'submit']},
        clear_dependencies={'on_change': ['mac_address', 'hostname', 'submit']},
        is_disabled_on_start=False
    )

    mac_address = CustomStringField(
        label='MAC Address',
        required=True,
        validators=[MacAddress()]
    )

    hostname = CustomStringField(
        label='Hostname',
        required=True
    )

    submit = SubmitField(label='Submit')
