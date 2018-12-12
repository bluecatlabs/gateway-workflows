# Copyright 2018 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys
import codecs

from flask import url_for, redirect, render_template, flash, g

from bluecat import route, util
import config.default_config as config
from main_app import app
from .cisco_aci_form import GenericFormTemplate


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/cisco_aci_example/cisco_aci_endpoint')
@util.workflow_permission_required('cisco_aci_page')
@util.exception_catcher
def cisco_aci_cisco_aci_page():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template(
        'cisco_aci_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/cisco_aci_example/form', methods=['POST'])
@util.workflow_permission_required('cisco_aci_page')
@util.exception_catcher
def cisco_aci_cisco_aci_page_form():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    if form.validate_on_submit():
        print(form.configuration.data)
        print(form.email.data)
        print(form.password.data)
        print(form.mac_address.data)
        print(form.ip_address.data)
        print(form.url.data)
        print(form.file.data)
        print(form.boolean_checked.data)
        print(form.boolean_unchecked.data)
        print(form.date_time.data)
        print(form.submit.data)

        # Put form processing code here
        g.user.logger.info('SUCCESS')
        flash('success', 'succeed')
        return redirect(url_for('cisco_acicisco_aci_cisco_aci_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'cisco_aci_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
