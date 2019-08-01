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


import io
import os
import re
import shutil
import sys
import zipfile
from datetime import datetime

import requests
from flask import url_for, redirect, render_template, flash, g

import config.default_config as config
from Administration.admin.workflow_export_import import get_workflow_path
from bluecat import route, util
from bluecat.internal.app_helper import load_permissions_json
from file_modified_handler import unload_modules_in_dir, remove_registered_workflow_functions
from main_app import app
from .gitlab_import_form import GenericFormTemplate
from . import gitlab_import_config, gitlab_import_util
from bluecat.util import get_password_from_file


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/gitlab_import/gitlab_import_endpoint')
@util.workflow_permission_required('gitlab_import_page')
@util.exception_catcher
def gitlab_import_gitlab_import_page():
    form = GenericFormTemplate()
    form.default_group.data = gitlab_import_config.default_group
    form.gitlab_groups.choices = gitlab_import_util.get_gitlab_groups(default_val=True)

    return render_template(
        'gitlab_import_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/gitlab_import/form', methods=['POST'])
@util.workflow_permission_required('gitlab_import_page')
@util.exception_catcher
def gitlab_import_gitlab_import_page_form():
    form = GenericFormTemplate()
    form.gitlab_groups.choices = gitlab_import_util.get_gitlab_groups(default_val=True)
    if form.validate_on_submit():

        try:
            # This is to get and download the archive zip
            response = {}
            response = requests.get(
                gitlab_import_config.gitlab_url + 'projects/' + str(
                    form.gitlab_groups.data) + '/repository/archive.zip?private_token=' + get_password_from_file(gitlab_import_config.secret_file), None)
            response.raise_for_status()
            print(
                "To download, use this link {}projects/{}/repository/archive.zip?private_token={} ".format(
                    gitlab_import_config.gitlab_url,
                    str(
                                                                                                               form.gitlab_groups.data),
                    get_password_from_file(gitlab_import_config.secret_file)))

            # Get the file name
            d = response.headers['content-disposition']
            file_name = re.findall("filename=(.+)", d)
            file_name = "".join(file_name)

            # Clean the file name up so we can use it for the foldername after unzipping
            folder_name = file_name.strip('\"').replace('.zip', '')

            with zipfile.ZipFile(io.BytesIO(response.content)) as thezip:
                thezip.extractall(gitlab_import_config.workflow_dir)

            gitlab_directories = list()

            ziped_dirs = os.path.join(gitlab_import_config.workflow_dir, folder_name, gitlab_import_config.gitlab_import_directory)
            dirs = os.listdir(ziped_dirs)

            time_format = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

            # Utils dir loading
            try:
                if gitlab_import_config.gitlab_import_utils_directory:
                    print("Found utils to load")
                    # Is the folder really there?
                    if os.path.exists(os.path.join("bluecat_portal", gitlab_import_config.gw_utils_directory)):
                        # Move folder from zip to deployed util dir
                        # backup folder
                        # Does the backup folder exist
                        if os.path.exists(os.path.join("bluecat_portal", (gitlab_import_config.backups_folder))):

                            # Create the backup file
                            shutil.make_archive(
                                os.path.join("bluecat_portal", gitlab_import_config.backups_folder) + '/' + gitlab_import_config.gitlab_import_utils_directory + '-' + time_format,
                                'zip', os.path.join("bluecat_portal", gitlab_import_config.gw_utils_directory))
                        else:
                            # Create backup folder
                            os.mkdir(os.path.join("bluecat_portal", gitlab_import_config.backups_folder))
                            shutil.make_archive(
                                os.path.join("bluecat_portal", gitlab_import_config.backups_folder) + '/' + gitlab_import_config.gitlab_import_utils_directory + '-' + time_format,
                                'zip', os.path.join("bluecat_portal", gitlab_import_config.gw_utils_directory))
                        # Delete the util folder on the GW server
                        shutil.rmtree(os.path.join("bluecat_portal", gitlab_import_config.gw_utils_directory))
                        # Move GitHub Util folder to GW server
                        shutil.move(
                            os.path.join(gitlab_import_config.workflow_dir, folder_name, gitlab_import_config.gitlab_import_utils_directory),
                            os.path.join("bluecat_portal", gitlab_import_config.gw_utils_directory.rsplit('/', 1)[0]))
                    else:
                        # Move folder from zip to deployed util dir
                        shutil.move(
                            os.path.join(gitlab_import_config.workflow_dir, folder_name, gitlab_import_config.gitlab_import_utils_directory),
                            os.path.join("bluecat_portal", gitlab_import_config.gw_utils_directory.rsplit('/', 1)[0]))

                else:
                    print("No utils specified in custom.gitlab_import_utils_directory")
                    app.logger.info("No util folder used")

            except Exception as e:
                app.logger.exception("Failed to load GitLab Util folder: {}".format(str(e)))
                g.user.logger.warning('%s' % util.safe_str(e), msg_type=g.user.logger.EXCEPTION)
                flash(
                    'Failed to load GitLab Util folder properly. Check to see if path ' + gitlab_import_config.gw_utils_directory + ' exists on the server.')
                return redirect(url_for('gitlab_importgitlab_import_gitlab_import_page'))

            # Create backup
            shutil.make_archive(
                os.path.join("bluecat_portal", gitlab_import_config.backups_folder) + '/' + gitlab_import_config.gitlab_import_directory + '-' + time_format,
                'zip', os.path.join(gitlab_import_config.workflow_dir, gitlab_import_config.gitlab_import_directory))

            for dir in dirs:
                # Workflow dir loading
                if os.path.isdir(os.path.join(gitlab_import_config.workflow_dir, folder_name, gitlab_import_config.gitlab_import_directory, dir)):
                    if os.path.exists(os.path.join(gitlab_import_config.workflow_dir, gitlab_import_config.gitlab_import_directory, dir)):
                        # Unregister existing mapped functions
                        for workflow_name, workflow_fields in list(config.workflows.items()):
                            if dir in workflow_fields['categories']:
                                app.logger.info("Unloading workflow %s", workflow_name)
                                workflow_path = get_workflow_path(workflow_name)
                                if not remove_registered_workflow_functions(workflow_path.replace(os.path.sep, '.')):
                                    raise Exception("Removal failed {}".format(workflow_path.replace(os.path.sep, '.')))
                                unload_modules_in_dir(workflow_path.replace(os.path.sep, '.'),
                                                      os.listdir(workflow_path))
                                config.workflows.pop(workflow_name)
                        shutil.rmtree(os.path.join(gitlab_import_config.workflow_dir, gitlab_import_config.gitlab_import_directory, dir))
                    shutil.move(os.path.join(gitlab_import_config.workflow_dir, folder_name, gitlab_import_config.gitlab_import_directory, dir),
                                os.path.join(gitlab_import_config.workflow_dir, gitlab_import_config.gitlab_import_directory))
                    gitlab_directories.append(dir)

            permissions = load_permissions_json()

            status = True
            # Refresh config.workflows
            for dir in gitlab_directories:
                if not gitlab_import_util.custom_workflow_navigator(os.path.join(gitlab_import_config.workflow_dir, gitlab_import_config.gitlab_import_directory, dir),
                                                                    permissions):
                    status = False

            if not status:
                raise Exception("Failed to load workflows in memory")
        # pylint: disable=broad-except
        except Exception as e:
            app.logger.exception("Failed to load GitLab workflows: {}".format(str(e)))
            g.user.logger.warning('%s' % util.safe_str(e), msg_type=g.user.logger.EXCEPTION)
            flash('Unable to import GitLab workflows properly: ' + util.safe_str(e))
            return redirect(url_for('gitlab_importgitlab_import_gitlab_import_page'))

        finally:
            if os.path.exists(os.path.join(gitlab_import_config.workflow_dir, folder_name)):
                shutil.rmtree(os.path.join(gitlab_import_config.workflow_dir, folder_name))

        g.user.logger.info('SUCCESS')
        flash('Imported GitLab workflows successfully', 'succeed')
        return redirect(url_for('gitlab_importgitlab_import_gitlab_import_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'gitlab_import_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
