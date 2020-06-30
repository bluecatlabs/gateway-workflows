# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: BlueCat Networks
# Date: 2019-05-15
# Gateway Version: 20.1.1
# Description: Certified Gateway workflows

"""
Cisco ACI form
"""
from wtforms.validators import DataRequired
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import (
    Configuration, CustomBooleanField, CustomPasswordField, CustomStringField,
    CustomSearchButtonField, TableField, PlainHTML, CustomButtonField
)


class SimpleButtonField(CustomButtonField):
    """Simple button class that works with UI Components."""

    def generate_populate_function_js(self):
        """
        Generate JavaScript for populate function.
        Generate empty populate function in case another js function
        tries to call the searchButtons populate function.

        :return: JavaScript for populate function.

        """
        return 'function populate_{id}(){{}}\n'.format(id=self.id)

    def generate_call_function_js(self):
        """
        Generate JavaScript for call function.

        :return: JavaScript for call function.

        """
        return 'function call_{id}(){{}}\n'.format(id=self.id)


# pylint: disable=unused-argument
def add_fabric(*args, **kwargs):
    """
    Returns the endpoint for importing the ACI fabric.
    :param args:
    :param kwargs:
    :return:
    """
    return 'import_fabric'


# pylint: disable=unused-argument
def get_tenants(*args, **kwargs):
    """
    Returns the endpoint for the view to call.
    :param args:
    :param kwargs:
    :return: Endpoint for view to call.
    """
    return 'form'


# pylint: disable=unused-argument
def import_tenants(*args, **kwargs):
    """
    Returns the endpoint for the view to call.
    :param args:
    :param kwargs:
    :return: Endpoint for view to call.
    """
    return 'import_tenants'


# pylint: disable=unused-argument
def raw_table_data(*args, checked=True, **kwargs):
    # pylint: disable=unused-argument
    """Returns table formatted data for display in the TableField component"""
    import_box = 'import_select_all'
    epd_box = 'import_endpoint_devices_select_all'
    ow_box = 'overwrite_select_all'
    checked_html = ''
    if checked:
        checked_html = 'checked'
    select_all_html = '<input type="checkbox" id="{name}" name="{name}" ' + checked_html + \
                      ' class="table_checkbox" onclick="select_all_in_column.call(this, {index})">'
    return {
        "columns": [
            {"title": "Tenant"},
            {"title": "{}<div>Import</div>".format(select_all_html.format(name=import_box, index=1))},
            {"title": "{}<div>Import Endpoint Devices</div>".format(select_all_html.format(name=epd_box, index=2))},
            {"title": "{}<div>Overwrite Existing</div>".format(select_all_html.format(name=ow_box, index=3))},
        ],
        "columnDefs": [{"width": "18%", "targets": [1, 2, 3]},
                       {"orderable": False, "targets": [1, 2, 3]}],
        'lengthMenu': [5, 20, 30, 40, 50, 100, 500, 1000],
        'escapeRender': [0],
        "sDom": '<"H"l<"check_all_button">fr>t<"F"ip>'
    }


class GenericFormTemplate(GatewayForm):
    """
    Cisco ACI form

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'cisco_aci'
    workflow_permission = 'cisco_aci_page'

    apic_ip = CustomStringField(
        label='APIC IP',
        required=True,
        default='',
        validators=[DataRequired()],
        is_disabled_on_start=False,
    )

    apic_username = CustomStringField(
        label='APIC USERNAME',
        default='',
        required=True,
        validators=[DataRequired()],
        is_disabled_on_start=False,
    )

    apic_password = CustomPasswordField(
        label='APIC PASSWORD',
        default='abc',
        validators=[DataRequired()],
        is_disabled_on_start=False,
    )

    optional = PlainHTML('<hr/><h4>OPTIONAL</h4><p>Import ACI Fabric only if you wish to import APIC, SPINE, and'
                         ' LEAF devices to the selected BAM configuration.</p><br/>')

    import_devices_checkbox = CustomBooleanField(
        label='Import ACI Fabric Devices to',
        on_checked=['enable_configuration'],
        on_unchecked=['disable_configuration', 'disable_import_fabric'],
        is_disabled_on_start=False,
    )

    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        coerce=int,
        label='',
        validators=[],
        enable_dependencies={'on_complete': ['import_fabric']},
        disable_dependencies={'on_change': ['import_fabric']},
        clear_below_on_change=False,
    )

    import_fabric = CustomSearchButtonField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='IMPORT FABRIC',
        default='IMPORT',
        server_side_method=add_fabric,
        display_message=True,
    )

    html = PlainHTML('<br/><br/><hr/>')

    discover = CustomSearchButtonField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='DISCOVER TENANTS',
        is_disabled_on_start=False,
        default='Search',
        on_complete=['call_output_table', 'add_checkall_button', 'add_on_page_change_listener'],
        server_side_method=get_tenants,
        display_message=True,
    )

    output_table = TableField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='',
        table_features=raw_table_data(),
        is_disabled_on_start=False,
    )

    import_tenants = SimpleButtonField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='IMPORT INFRASTRUCTURE',
        is_disabled_on_start=False,
        default='Search',
    )
