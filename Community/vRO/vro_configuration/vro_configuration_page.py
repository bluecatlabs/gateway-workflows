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
from .vro_configuration_form import GenericFormTemplate
from . import vro_config

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/vro_configuration/vro_configuration_endpoint')
@util.workflow_permission_required('vro_configuration_page')
@util.exception_catcher
def vro_configuration_vro_configuration_page():
    form = GenericFormTemplate()
    form.default_configuration.data = vro_config.default_configuration
    form.default_view.data = vro_config.default_view
    form.default_zone.data = vro_config.default_zone
    form.default_reverse_flag.data = vro_config.default_reverse_flag

    return render_template(
        'vro_configuration_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/vro_configuration/form', methods=['POST'])
@util.workflow_permission_required('vro_configuration_page')
@util.exception_catcher
def vro_configuration_vro_configuration_page_form():
    form = GenericFormTemplate()

    if form.validate_on_submit():
        with open(os.path.join('bluecat_portal', 'workflows', 'vRO', 'vro_configuration', 'vro_config.py'), 'r') as config_file:
            content = config_file.read()

        config_data = dict(request.form.items())
        data_to_log = dict((key, value) for key, value in config_data.items())
        g.user.logger.info('The following changes are about to be written to mail and db config file: %s' % data_to_log)

        user_config = importlib.import_module('bluecat_portal.workflows.vRO.vro_configuration.vro_config')

        for key, value in config_data.items():
            if not hasattr(vro_config, key):
                continue
            setattr(vro_config, key, value)
            if type(value).__name__ == 'str':
                value_string = '{}'.format([value])
                replace_string = '{} = {}'.format(key, value_string[1:-1])
            else:
                replace_string = "%s = %s" % (key, value)

            if hasattr(user_config, key):
                content = re.sub("^%s = .+$" % key, replace_string, content, flags=re.MULTILINE)
            else:
                content = content + replace_string + '\n'

        with open(os.path.join('bluecat_portal', 'workflows', 'vRO', 'vro_configuration', 'vro_config.py'), 'w') as config_file:
            config_file.write(content)

        g.user.logger.info('SUCCESS')
        flash('Saved form data to file', 'succeed')
        return redirect(url_for('vro_configurationvro_configuration_vro_configuration_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'vro_configuration_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
