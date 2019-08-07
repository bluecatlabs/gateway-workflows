# Copyright 2019 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys
import codecs
import importlib
import re

from flask import url_for, redirect, render_template, flash, g, request

from bluecat import route, util
import config.default_config as config
from . import service_requests_config
from main_app import app
from .configure_service_requests_form import GenericFormTemplate


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/configure_service_requests/configure_service_requests_endpoint')
@util.workflow_permission_required('configure_service_requests_page')
@util.exception_catcher
def configure_service_requests_configure_service_requests_page():
    form = GenericFormTemplate()
    form.servicenow_url.data = service_requests_config.servicenow_url
    form.servicenow_username.data = service_requests_config.servicenow_username
    form.servicenow_secret_file = service_requests_config.servicenow_secret_file

    return render_template(
        'configure_service_requests_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/configure_service_requests/form', methods=['POST'])
@util.workflow_permission_required('configure_service_requests_page')
@util.exception_catcher
def configure_service_requests_configure_service_requests_page_form():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration

    if form.validate_on_submit():
        # Check Gateway Secret file and path
        secret_ok = os.path.isfile(os.path.join("bluecat_portal", (form.servicenow_secret_file.data)))

        if not secret_ok:
            g.user.logger.info('Form data was not valid.')
            app.logger.exception(
                "The secret file or path: {} doesn\'t exist on the server".format(os.path.join("bluecat_portal", (form.servicenow_secret_file.data))))
            flash('The secret file or path ' + os.path.join("bluecat_portal", (form.servicenow_secret_file.data)) + ' doesn\'t exist on the server')
            return render_template(
                'configure_service_requests_page.html',
                form=form,
                text=util.get_text(module_path(), config.language),
                options=g.user.get_options(),
            )

        with open(os.path.join('bluecat_portal', 'workflows', 'Service Requests', 'configure_service_requests', 'service_requests_config.py'), 'r') as config_file:
            content = config_file.read()

        config_data = dict(request.form.items())
        data_to_log = dict((key, value) for key, value in config_data.items())
        g.user.logger.info('The following changes are about to be written to mail and db config file: %s' % data_to_log)

        user_config = importlib.import_module('bluecat_portal.workflows.Service Requests.configure_service_requests.service_requests_config')

        for key, value in config_data.items():
            if not hasattr(service_requests_config, key):
                continue
            setattr(service_requests_config, key, value)
            if type(value).__name__ == 'str':
                value_string = '{}'.format([value])
                replace_string = '{} = {}'.format(key, value_string[1:-1])
            else:
                replace_string = "%s = %s" % (key, value)

            if hasattr(user_config, key):
                content = re.sub("^%s = .+$" % key, replace_string, content, flags=re.MULTILINE)
            else:
                content = content + replace_string + '\n'

        with open(os.path.join('bluecat_portal', 'workflows', 'Service Requests', 'configure_service_requests', 'service_requests_config.py'), 'w') as config_file:
            config_file.write(content)


        g.user.logger.info('SUCCESS')
        flash('success', 'succeed')
        return redirect(url_for('configure_service_requestsconfigure_service_requests_configure_service_requests_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'configure_service_requests_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
