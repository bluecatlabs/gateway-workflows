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

from wtforms import FileField, SubmitField, BooleanField
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, PlainHTML


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'bulk'
    workflow_permission = 'bulk'
    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Configuration',
        required=True,
        coerce=int,
        validators=[],
        is_disabled_on_start=False,
        #on_complete=['call_view'],
        #enable_on_complete=['view'],
        #To add view, uncomment the above two, comment out the one below
        enable_on_complete=['file'],
        clear_below_on_change=True
    )

    #Uncomment
    """view = View(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='View',
        required=True,
        enable_on_complete=['file']
    )"""

    file = FileField(
        label='Bulk Add File'
    )

    download_link = PlainHTML(
        "<a id='template_download_link' href='/bulk/download/template.csv' download>Template Download Link</a>")

    submit = SubmitField(label='Process')