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
# Date: 2021-05-04
# Gateway Version: 20.6.1
# Description: Example Gateway workflow

"""
Add text record form
"""
from wtforms import SubmitField
from bluecat.wtform_fields import Configuration, View, Zone, CustomStringField
from bluecat.wtform_extensions import GatewayForm


class GenericFormTemplate(GatewayForm):
    """ Form to generate HTML and Javascript for the add_text_record workflow

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'add_text_record'
    workflow_permission = 'add_text_record_page'
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
        enable_dependencies={'on_complete': ['name', 'text', 'submit']},
        disable_dependencies={'on_change': ['name', 'text', 'submit']},
        clear_dependencies={'on_change': ['name', 'text']},
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True
    )

    name = CustomStringField(
        label='Name'
    )

    text = CustomStringField(
        label='Text'
    )

    submit = SubmitField(label='Submit')
