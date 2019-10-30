# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from wtforms import SubmitField
from wtforms.validators import DataRequired
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, PlainHTML


class GenericFormTemplate(GatewayForm):
    workflow_name = 'cache_example'
    workflow_permission = 'cache_example_page'
    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Configuration',
        required=True,
        coerce=int,
        validators=[],
        is_disabled_on_start=False,
        enable_on_complete=['ip_network', 'submit'],
        clear_below_on_change=False
    )

    ip_network = CustomStringField(
        label='Network',
        validators=[DataRequired()]
    )

    display = PlainHTML(
        "<div id='data_display' />"
    )

    submit = SubmitField(
        label='Submit'
    )
