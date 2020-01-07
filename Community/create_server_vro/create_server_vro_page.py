# Copyright 2020 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys
import codecs

from flask import url_for, redirect, render_template, flash, g

from bluecat import route, util
import config.default_config as config
from main_app import app
from .create_server_vro_form import GenericFormTemplate

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/create_server_vro/create_server_vro_endpoint')
@util.workflow_permission_required('create_server_vro_page')
@util.exception_catcher
def create_server_vro_create_server_vro_page():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template(
        'create_server_vro_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/create_server_vro/form', methods=['POST'])
@util.workflow_permission_required('create_server_vro_page')
@util.exception_catcher
def create_server_vro_create_server_vro_page_form():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    if form.validate_on_submit():

        configuration = g.user.get_api().get_entity_by_id(form.configuration.data)
        view = configuration.get_view(form.view.data)
        network = form.ip4_network.data.split('/')
        network = configuration.get_ip_range_by_ip('IP4Network', network[0])

        props = {'excludeDHCPRange': 'True'}
        hostinfo = util.safe_str(form.hostname.data) + '.' + util.safe_str(form.zone.data) + ',' + util.safe_str(view.get_id()) + ',' + 'True' + ',' + 'False'

        assigned_ip = network.assign_next_available_ip4_address(form.mac_address.data, hostinfo, 'MAKE_DHCP_RESERVED',
                                                                properties=props)

        absoluteName = form.hostname.data + '.' + form.zone.data

        g.user.logger.info('Success - Host (A) Record ' + absoluteName + ' IP Address: ' + util.safe_str(assigned_ip.get_property('address')) + ' State: ' + util.safe_str(assigned_ip.get_property('state')) + ' Mac Address: ' + util.safe_str(assigned_ip.get_property('macAddress')))
        flash('Success - Host (A) Record ' + absoluteName + ' IP Address: ' + util.safe_str(assigned_ip.get_property('address')) + ' State: ' + util.safe_str(assigned_ip.get_property('state')) + ' Mac Address: ' + util.safe_str(assigned_ip.get_property('macAddress')), 'succeed')
        return redirect(url_for('create_server_vrocreate_server_vro_create_server_vro_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'create_server_vro_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
