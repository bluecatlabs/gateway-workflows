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
from wtforms.validators import DataRequired, URL
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomStringField


class EdgeForm(GatewayForm):

    workflow_name = 'hello_edge'
    workflow_permission = 'hello_edge_page'

    edge = CustomStringField(
        label='Edge CI',
        default='https://api.edge.example.com',
        validators=[DataRequired(), URL()],
        is_disabled_on_start=False
    )

    client = CustomStringField(
        label='Client ID',
        default='',
        validators=[DataRequired()],
        is_disabled_on_start=False
    )

    client_secret = CustomStringField(
        label='Client Secret',
        default='',
        validators=[DataRequired()],
        is_disabled_on_start=False
    )


    submit = SubmitField(label='Submit')
