# Copyright 2019 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys
import importlib
import re

from flask import render_template, flash, g, request

from bluecat import route, util
import config.default_config as config
from main_app import app
from .gitlab_configuration_form import GenericFormTemplate
from ..gitlab_import import gitlab_import_config


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/gitlab_configuration/gitlab_configuration_endpoint')
@util.workflow_permission_required('gitlab_configuration_page')
@util.exception_catcher
def gitlab_configuration_gitlab_configuration_page():
    form = GenericFormTemplate()

    form.gitlab_url.data = gitlab_import_config.gitlab_url
    form.default_group.data = gitlab_import_config.default_group
    form.gw_utils_directory.data = gitlab_import_config.gw_utils_directory
    form.backups_folder.data = gitlab_import_config.backups_folder
    form.gitlab_import_utils_directory.data = gitlab_import_config.gitlab_import_utils_directory
    form.gw_utils_directory.data = gitlab_import_config.gw_utils_directory
    form.gitlab_import_directory.data = gitlab_import_config.gitlab_import_directory

    return render_template(
        'gitlab_configuration_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/gitlab_configuration/form', methods=['POST'])
@util.workflow_permission_required('gitlab_configuration_page')
@util.exception_catcher
def gitlab_configuration_gitlab_configuration_page_form():
    form = GenericFormTemplate()

    if form.validate_on_submit():

        # Gateway Util Directory
        gw_utils_ok = os.path.exists(os.path.join("bluecat_portal", form.gw_utils_directory.data))

        if not gw_utils_ok:
            g.user.logger.info('Form data was not valid.')
            app.logger.exception(
                "The Util directory: {} doesn\'t exist on the server".format(form.gw_utils_directory.data))
            flash('The Util directory ' + form.gw_utils_directory.data + ' doesn\'t exist on the server')
            return render_template(
                'gitlab_configuration_page.html',
                form=form,
                text=util.get_text(module_path(), config.language),
                options=g.user.get_options(),
            )

        # Check Gateway Backup Folder
        bkp_ok = os.path.exists(os.path.join("bluecat_portal", form.backups_folder.data))

        if not bkp_ok:
            g.user.logger.info('Form data was not valid.')
            app.logger.exception(
                "The backup directory: {} doesn\'t exist on the server".format(form.backups_folder.data))
            flash('The backup directory ' + form.backups_folder.data + ' doesn\'t exist on the server')
            return render_template(
                'gitlab_configuration_page.html',
                form=form,
                text=util.get_text(module_path(), config.language),
                options=g.user.get_options(),
            )

        # Check Gateway Secret file and path
        secret_ok = os.path.isfile(os.path.join("bluecat_portal", (form.secret_file.data)))

        if not secret_ok:
            g.user.logger.info('Form data was not valid.')
            app.logger.exception(
                "The secret file or path: {} doesn\'t exist on the server".format(os.path.join("bluecat_portal", (form.secret_file.data))))
            flash('The secret file or path ' + os.path.join("bluecat_portal", (form.secret_file.data)) + ' doesn\'t exist on the server')
            return render_template(
                'gitlab_configuration_page.html',
                form=form,
                text=util.get_text(module_path(), config.language),
                options=g.user.get_options(),
            )

        with open(os.path.join('bluecat_portal', 'workflows', 'GitLab Management', 'gitlab_import', 'gitlab_import_config.py'), 'r') as config_file:
            content = config_file.read()

        config_data = dict(request.form.items())
        data_to_log = dict((key, value) for key, value in config_data.items())
        g.user.logger.info('The following changes are about to be written to mail and db config file: %s' % data_to_log)

        user_config = importlib.import_module('bluecat_portal.workflows.GitLab Management.gitlab_import.gitlab_import_config')

        for key, value in config_data.items():
            if not hasattr(gitlab_import_config, key):
                continue
            setattr(gitlab_import_config, key, value)
            if type(value).__name__ == 'str':
                value_string = '{}'.format([value])
                replace_string = '{} = {}'.format(key, value_string[1:-1])
            else:
                replace_string = "%s = %s" % (key, value)

            if hasattr(user_config, key):
                content = re.sub("^%s = .+$" % key, replace_string, content, flags=re.MULTILINE)
            else:
                content = content + replace_string + '\n'

        with open(os.path.join('bluecat_portal', 'workflows', 'GitLab Management', 'gitlab_import', 'gitlab_import_config.py'), 'w') as config_file:
            config_file.write(content)

        g.user.logger.info('SUCCESS')
        flash('success', 'succeed')
        return render_template(
            'gitlab_configuration_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )

    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'gitlab_configuration_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
