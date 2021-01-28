# Copyright 2020 BlueCat Networks. All rights reserved.
import os
import sys
import codecs

from flask import url_for, redirect, render_template, flash, g, request

from bluecat import route, util
import config.default_config as config
from main_app import app
from .add_dual_stack_host_form import GenericFormTemplate


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/add_dual_stack_host/add_dual_stack_host_endpoint')
@util.workflow_permission_required('add_dual_stack_host_page')
@util.exception_catcher
@util.ui_secure_endpoint
def add_dual_stack_host_add_dual_stack_host_page():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template(
        'add_dual_stack_host_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/add_dual_stack_host/form', methods=['POST'])
@util.workflow_permission_required('add_dual_stack_host_page')
@util.exception_catcher
@util.ui_secure_endpoint
def add_dual_stack_host_add_dual_stack_host_page_form():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)

    address_list = []
    if form.validate_on_submit():
        try:
            # Retrieve form attributes
            configuration = g.user.get_api().get_entity_by_id(form.configuration.data)
            view = configuration.get_view(request.form['view'])
            absolute_name = form.hostname.data + '.' + request.form['zone']
            ip4_address = request.form['ip_address']
            ip6_address = request.form['ip6_address']

            # Add IP4 and IP6 addresses to address list
            address_list.append(ip4_address)
            address_list.append(ip6_address)
            add_device = request.form.get('add_device') # Must use 'get' otherwise returns a 400 error on False

            # Add Host Record
            host_record = view.add_host_record(absolute_name, address_list)

            # Optionally Add Device
            if add_device:
                device_id = g.user.get_api()._api_client.service.addDevice(
                    configurationId=form.configuration.data, deviceSubtypeId='0', deviceTypeId='0',
                    ip4Addresses=ip4_address, ip6Addresses=ip6_address, name=form.hostname.data
                )
                device_name = g.user.get_api().get_entity_by_id(device_id).get_name()
                g.user.logger.info('Success - Device ' + device_name +
                                ' added with Object ID: ' + util.safe_str(device_id))
                flash('Success - Device ' + device_name +
                    ' added with Object ID: ' + util.safe_str(device_id), 'succeed')

            # Put form processing code here
            g.user.logger.info('Success - Host (A & AAAA) Record ' + host_record.get_property('absoluteName') +
                               ' added with Object ID: ' + util.safe_str(host_record.get_id()))

            flash('Success - Host (A & AAAA) Record ' + host_record.get_property('absoluteName') +
                  ' added with Object ID: ' +
                  util.safe_str(host_record.get_id()), 'succeed')


            return redirect(url_for('add_dual_stack_hostadd_dual_stack_host_add_dual_stack_host_page'))
        except Exception as e:
            flash(util.safe_str(e))
            # Log error and render workflow page
            g.user.logger.warning('%s' % util.safe_str(e), msg_type=g.user.logger.EXCEPTION)
            return render_template('add_dual_stack_host_page.html',
                                   form=form,
                                   text=util.get_text(module_path(), config.language),
                                   options=g.user.get_options())

    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'add_dual_stack_host_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
