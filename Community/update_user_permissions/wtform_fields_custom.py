# Copyright 2017 BlueCat Networks (USA) Inc. and its affiliates
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# By: Bill Morton (bmorton@bluecatnetworks.com)
# Date: 06-12-2017
# Gateway Version: 17.10.1
# Copyright 2017 BlueCat Networks. All rights reserved.
"""
Custom WTForm fields.
"""

from bluecat.ui_components.wtform_widgets import SuperSelect

from .util_custom import get_groups
from bluecat.wtform_fields import CustomSelectField

class Group(CustomSelectField):
    """
    SelectField that is autopopulated with group data.
    """
    widget = SuperSelect()

    def __init__(self, label=None, validators=None, **kwargs):
        if not label:
            label = 'Group'
        super(Group, self).__init__(label=label, validators=validators,
                                            choices_function=get_groups,
                                            **kwargs)