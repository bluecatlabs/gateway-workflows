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

import requests

import os
from bluecat.internal.app_helper import refresh_workflow, workflow_navigator
from main_app import app
from . import gitlab_import_config
from flask import g, flash


def get_gitlab_groups(default_val=False):
    """
    Get a list of groups for display in a drop-down menu box.

    :return: List of groups name tuples.
    """
    try:
        groups = requests.get(gitlab_import_config.url + 'groups?search=' + gitlab_import_config.default_group + '&private_token=' + gitlab_import_config.personal_token, None)

    except Exception as e:
        flash('An error occured! Please check the user logs for the current session for more information.')

    if groups.status_code == 200:

        groups = groups.json()

        for group in groups:
            group_id = group['id']
        projects = requests.get(
            gitlab_import_config.url + 'groups/' + str(group_id) + '/projects?include_subgroups=True&private_token=' + gitlab_import_config.personal_token + '&per_page=100', None)
        projects = projects.json()

        projects.sort(key=lambda x: x['path_with_namespace'], reverse=False)

        result = []

        if default_val:
            result.append(('1', 'Please Select'))

        for project in projects:
            result.append((project['id'], project['path_with_namespace'].rpartition('/')[-0] + '/' + project['name']))
        return result

    else:
        result =[('1', 'Not Connected! Check logs for more detail')]
        g.user.logger.warning("Failed to connect to GitLab with the following configurations: url: {}, default_group {}, personal token {}".format(gitlab_import_config.url, gitlab_import_config.default_group, gitlab_import_config.personal_token), msg_type=g.user.logger.EXCEPTION)

    return result


def get_gitlab_groups_old(default_val=False):
    """
    Get a list of groups for display in a drop-down menu box.

    :return: List of groups name tuples.
    """
    groups = requests.get(gitlab_import_config.url + 'groups?search=' + gitlab_import_config.default_group + '&private_token=' + gitlab_import_config.personal_token, None)
    groups = groups.json()
    for group in groups:
        group_id = group['id']
    projects = requests.get(
        gitlab_import_config.url + 'groups/' + str(group_id) + '/projects?include_subgroups=True&private_token=' + gitlab_import_config.personal_token + '&per_page=100', None)
    projects = projects.json()

    projects.sort(key=lambda x: x['path_with_namespace'], reverse=False)

    result = []

    if default_val:
        result.append(('1', 'Please Select'))

    for project in projects:
        result.append((project['id'], project['path_with_namespace'].rpartition('/')[-0] + '/' + project['name']))
    return result

def get_group_id(selected_group):
    selected_project_datas = requests.get(
        gitlab_import_config.url + 'projects?search=' + selected_group + '&private_token=' + gitlab_import_config.personal_token, None)

    groups = selected_project_datas.json()

    result = []

    for group in groups:
        result.append(group['id'])

    return result


def custom_workflow_navigator(workflow_dir, permissions, builtin=False):
    """ reloads workflows if user has permissions to them"""

    status = True
    for workflow_name in os.listdir(os.path.join(gitlab_import_config.workflow_dir, gitlab_import_config.gitlab_import_directory)):
        if os.path.isfile('%s/%s/__init__.py' % (os.path.join(gitlab_import_config.workflow_dir, gitlab_import_config.gitlab_import_directory), workflow_name)):
            if workflow_name in permissions:
                page_permissions = permissions[workflow_name]
            else:
                page_permissions = {}

            try:
                result = refresh_workflow(os.path.join(gitlab_import_config.workflow_dir, gitlab_import_config.gitlab_import_directory), workflow_name, page_permissions, builtin)
            # pylint: disable=broad-except
            except Exception as e:
                app.logger.error("Failed to load workflow %s, error was %s", workflow_name, str(e))
                status = False
                continue

            if result:
                branch_dir = os.path.join(os.path.join(gitlab_import_config.workflow_dir, gitlab_import_config.gitlab_import_directory), workflow_name)
                if not os.path.isfile(branch_dir):
                    if not workflow_navigator(branch_dir, permissions, builtin):
                        status = False

    return status

