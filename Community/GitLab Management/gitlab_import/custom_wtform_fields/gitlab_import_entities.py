# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2019-07-01
# Gateway Version: 19.5.1
# Description: Community Gateway workflow

"""
UI components for BAM entities
"""

# Import Javascript Helpers
from bluecat.ui_components.wtform_widgets import SuperSelect
from bluecat.wtform_fields.custom_select_field import CustomSelectField
from ..gitlab_import_util import get_gitlab_groups


class GitlabGroups(CustomSelectField):
    """
    SelectField that is auto-populated with configuration data.

    :param label: HTML label for the generated field.
    :param validators: WTForm validators for the field run on the server side.
    :param kwargs: Other keyword arguments for WTForms Fields.

    """
    widget = SuperSelect()

    def __init__(self, label='GitLab', validators=None, **kwargs):
        """ Pass parameters to CustomSelectField for initialization.
        """
        super(GitlabGroups, self).__init__(
            label,
            validators,
            choices_function=get_gitlab_groups,
            **kwargs
        )

