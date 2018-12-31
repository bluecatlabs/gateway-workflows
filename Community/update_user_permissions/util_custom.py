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
Useful Functions
"""
from flask import g


def get_groups(default_val=False):
    """
    Get a list of user groups for display in a dropdown box.

    :return: List of group ID, group name tuples.
    """
    result = []
    if g.user:
        if default_val:
            result.append(('1', 'Please Select'))
            groups = g.user.get_api().get_by_object_types('*', ['UserGroup'])
        for gr in groups:
            result.append((gr.get_id(), gr.get_name()))
    return result


def get_udf_portal_groups():
    udfs = g.user.get_api()._api_client.service.getUserDefinedFields('User', "False")
    group_values = []
    for udf in udfs.item:
        if udf['name'] == 'PortalGroup' and udf['predefinedValues']:
            for group_value in udf['predefinedValues'].split('|'):
                if group_value != '':
                    group_values.append((group_value, group_value))
            break

    return group_values