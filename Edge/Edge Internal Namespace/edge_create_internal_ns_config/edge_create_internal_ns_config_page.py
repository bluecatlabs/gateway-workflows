# Copyright 2019 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys
import importlib
import re

from flask import url_for, redirect, render_template, flash, g, request

from bluecat import route, util
import config.default_config as config
from main_app import app
from .edge_create_internal_ns_config_form import GenericFormTemplate
from . import edge_create_internal_ns_configuration


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/edge_create_internal_ns_config/edge_create_internal_ns_config_endpoint')
@util.workflow_permission_required('edge_create_internal_ns_config_page')
@util.exception_catcher
def edge_create_internal_ns_config_edge_create_internal_ns_config_page():
    form = GenericFormTemplate()

    form.default_configuration.data = edge_create_internal_ns_configuration.default_configuration
    form.default_view.data = edge_create_internal_ns_configuration.default_view
    form.domain_list_file.data = edge_create_internal_ns_configuration.domain_list_file
    form.edge_url.data = edge_create_internal_ns_configuration.edge_url
    form.client_id.data = edge_create_internal_ns_configuration.client_id
    form.clientSecret.data = edge_create_internal_ns_configuration.clientSecret

    return render_template(
        'edge_create_internal_ns_config_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/edge_create_internal_ns_config/form', methods=['POST'])
@util.workflow_permission_required('edge_create_internal_ns_config_page')
@util.exception_catcher
def edge_create_internal_ns_config_edge_create_internal_ns_config_page_form():
    form = GenericFormTemplate()

    if form.validate_on_submit():
        with open(os.path.join('bluecat_portal', 'workflows', 'Edge', 'Edge Internal Namespace', 'edge_create_internal_ns_config', 'edge_create_internal_ns_configuration.py'), 'r') as config_file:
            content = config_file.read()

        config_data = dict(request.form.items())
        data_to_log = dict((key, value) for key, value in config_data.items())
        g.user.logger.info('The following changes are about to be written to mail and db config file: %s' % data_to_log)

        user_config = importlib.import_module('bluecat_portal.workflows.Edge.Edge Internal Namespace.edge_create_internal_ns_config.edge_create_internal_ns_configuration')

        for key, value in config_data.items():
            if not hasattr(edge_create_internal_ns_configuration, key):
                continue
            setattr(edge_create_internal_ns_configuration, key, value)
            if type(value).__name__ == 'str':
                value_string = '{}'.format([value])
                replace_string = '{} = {}'.format(key, value_string[1:-1])
            else:
                replace_string = "%s = %s" % (key, value)

            if hasattr(user_config, key):
                content = re.sub("^%s = .+$" % key, replace_string, content, flags=re.MULTILINE)
            else:
                content = content + replace_string + '\n'

        with open(os.path.join('bluecat_portal', 'workflows', 'Edge', 'Edge Internal Namespace', 'edge_create_internal_ns_config', 'edge_create_internal_ns_configuration.py'), 'w') as config_file:
            config_file.write(content)

        # Put form processing code here
        g.user.logger.info('SUCCESS')
        flash('success', 'succeed')
        return redirect(url_for('edge_create_internal_ns_configedge_create_internal_ns_config_edge_create_internal_ns_config_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'edge_create_internal_ns_config_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )

