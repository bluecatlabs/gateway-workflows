# Copyright 2020 BlueCat Networks. All rights reserved.
import os
import sys
import codecs

from flask import url_for, redirect, render_template, flash, g, request

from bluecat import route, util
from bluecat.ip4_address import IP4Address
import config.default_config as config
from main_app import app
from ipaddress import IPv6Network, IPv6Address
from random import seed, getrandbits
from .add_next_available_dual_stack_host_form import GenericFormTemplate


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


def get_next_available_ip6_address(subnet, config, tries=100):
    """
    Get the next available address within an IPv6 network
    in a /64 subnet with 20k existing IPs, the chance of a conflict in a roll of the dice is 0.0000000000000001%
    :param: Subnet in which to find the next available address
    :param: Parent configuration
    :param: Number of tries before conflict
    :return: Address
    """
    for i in range(tries):
        address = get_random_ip6_address(subnet)
        try:
            config.get_ip6_address(address)
        except:
            return address
    return None


def get_random_ip6_address(subnet):
    """
    :param: Chosen subnet in which to find an address
    :return: IPv6 Address Object
    """
    subnet = str(subnet) if isinstance(subnet, str) else subnet
    seed()
    network = IPv6Network(subnet)
    return IPv6Address(network.network_address + getrandbits(network.max_prefixlen - network.prefixlen))

# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/add_next_available_dual_stack_host/add_next_available_dual_stack_host_endpoint')
@util.workflow_permission_required('add_next_available_dual_stack_host_page')
@util.exception_catcher
@util.ui_secure_endpoint
def add_next_available_dual_stack_host_add_next_available_dual_stack_host_page():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template(
        'add_next_available_dual_stack_host_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/add_next_available_dual_stack_host/form', methods=['POST'])
@util.workflow_permission_required('add_next_available_dual_stack_host_page')
@util.exception_catcher
@util.ui_secure_endpoint
def add_next_available_dual_stack_host_add_next_available_dual_stack_host_page_form():
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
            ip4_network = configuration.get_ip_ranged_by_ip('IP4Network', request.form['ip4_network'].split('/'))
            ip6_network = request.form['ip6_network']
            na_ip4_address= ip4_network.get_next_available_ip4_address()
            na_ip6_address = str(get_next_available_ip6_address(ip6_network, configuration))
            address_list.append(na_ip4_address)
            address_list.append(na_ip6_address)
            add_device = request.form.get('add_device') # Must use 'get' otherwise returns a 400 error on False

            # Add Host Record
            host_record = view.add_host_record(absolute_name, address_list)

            # Add Optional Device
            if add_device:
                device_id = g.user.get_api()._api_client.service.addDevice(
                    configurationId=form.configuration.data, deviceSubtypeId='0', deviceTypeId='0',
                    ip4Addresses=na_ip4_address, ip6Addresses=na_ip6_address, name=form.hostname.data
                )
                device_name = g.user.get_api().get_entity_by_id(device_id).get_name()
                g.user.logger.info('Success - Device ' + device_name +
                                   ' added with Object ID: ' + util.safe_str(device_id))
                flash('Success - Device ' + device_name +
                      ' added with Object ID: ' + util.safe_str(device_id), 'succeed')

            g.user.logger.info('Success - Host (A & AAAA) Record ' + host_record.get_property('absoluteName') +
                               ' added with Object ID: ' + util.safe_str(host_record.get_id()))

            flash('Success - Host (A & AAAA) Record ' + host_record.get_property(
                'absoluteName') + ' added with Object ID: ' +
                  util.safe_str(host_record.get_id()), 'succeed')

            return redirect(url_for('add_next_available_dual_stack_hostadd_next_available_dual_stack_host_'
                                    'add_next_available_dual_stack_host_page'))


        except Exception as e:
            flash(util.safe_str(e))
            # Log error and render workflow page
            g.user.logger.warning('%s' % util.safe_str(e), msg_type=g.user.logger.EXCEPTION)
            return render_template('add_next_available_dual_stack_host_page.html',
                                   form=form,
                                   text=util.get_text(module_path(), config.language),
                                   options=g.user.get_options())
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'add_next_available_dual_stack_host_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
