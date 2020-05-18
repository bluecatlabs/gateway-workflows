# Copyright 2020 BlueCat Networks. All rights reserved.
import os
import sys

from flask import url_for, redirect, render_template, flash, g

from bluecat import route, util
import config.default_config as config
from main_app import app
from .add_mac_address_form import GenericFormTemplate
from bluecat.api_exception import PortalException, BAMException


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/add_mac_address/add_mac_address_endpoint')
@util.workflow_permission_required('add_mac_address_page')
@util.exception_catcher
def add_mac_address_add_mac_address_page():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template(
        'add_mac_address_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/add_mac_address/form', methods=['POST'])
@util.workflow_permission_required('add_mac_address_page')
@util.exception_catcher
def add_mac_address_add_mac_address_page_form():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    if form.validate_on_submit():
        # Retrieve configuration and view
        try:
            configuration = g.user.get_api().get_entity_by_id(form.configuration.data)
        except PortalException as e:
            g.user.logger.warning('%s' % e, msg_type=g.user.logger.EXCEPTION)
            flash('Configuration %s undefined in BAM' % form.configuration.data)
            return render_template(
                'add_mac_address_page.html',
                form=form,
                text=util.get_text(module_path(), config.language),
                options=g.user.get_options(),
            )

        # Check if mac address pool has been specified
        if form.mac_pool_boolean.data:
            try:
               mac_pool = g.user.get_api()._api_client.service.getEntityByName(configuration.get_id(), form.mac_pool.data, 'MACPool')
            except Exception as e:
                g.user.logger.error('%s' % e, msg_type=g.user.logger.EXCEPTION)
                flash('Unable to retrieve MAC Pool: %s with error: %s' % (form.mac_pool.data, util.safe_str(e)))
                return render_template(
                    'add_mac_address_page.html',
                    form=form,
                    text=util.get_text(module_path(), config.language),
                    options=g.user.get_options(),
                )

            # Instantiate mac pool object to a Gateway object
            mac_pool = g.user.get_api().instantiate_entity(mac_pool)
        else:
            mac_pool = ''

        # Add MAC address
        try:
            mac_address = configuration.add_mac_address(form.mac_address.data, form.mac_address_name.data, mac_pool)
        except BAMException as e:
            g.user.logger.error('%s' % e, msg_type=g.user.logger.EXCEPTION)
            if 'Duplicate of another item' in util.safe_str(e):
                flash('MAC Address %s is a duplicate of an existing MAC in Address Manager' % form.mac_address.data)
            else:
                flash('Unable to add MAC Address with error: %s' % util.safe_str(e))
            return render_template(
                'add_mac_address_page.html',
                form=form,
                text=util.get_text(module_path(), config.language),
                options=g.user.get_options(),
            )

        # Display success message
        if form.mac_pool_boolean.data:
            flash('MAC Address: %s has been successfully added with object ID: %s and to MAC Pool: %s'
                  % (form.mac_address.data, mac_address.get_id(), form.mac_pool.data), 'succeed')
        else:
            flash('MAC Address: %s has been successfully added to BAM with object ID: %s'
                  % (form.mac_address.data, mac_address.get_id()), 'succeed')

        return redirect(url_for('add_mac_addressadd_mac_address_add_mac_address_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'add_mac_address_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
