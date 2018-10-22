# Copyright 2018 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys
import ipaddress

from flask import render_template, g, request, jsonify
from flask_mail import Mail, Message

from bluecat import route, util
from bluecat.api_exception import APIException
import config.default_config as config
from main_app import app
from .SubnetStatus_form import GenericFormTemplate


def module_path():
    return os.path.dirname(os.path.abspath(str(__file__)))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/SubnetStatus/SubnetStatus_endpoint')
@util.workflow_permission_required('SubnetStatus_page')
@util.exception_catcher
def SubnetStatus_SubnetStatus_page():
    form = GenericFormTemplate()

    return render_template(
        'SubnetStatus_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/SubnetStatus/form', methods=['POST'])
@util.workflow_permission_required('SubnetStatus_page')
@util.exception_catcher
def SubnetStatus_SubnetStatus_page_form():
    form = GenericFormTemplate()

    data = run_stats_common(form.subnet.data)

    email_report(form.email.data, data['report'])

    return render_template(
        'SubnetStatus_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),)


def email_report(email, report):
    # Create email message for the form administrator and requestor
    email_message = """
        <html>
        <head></head>
            <body>
            %s
            </body>
        </html>
        """ % report

    # Send email message to admin
    mail = Mail(app)
    recipients = [email]
    msg = Message(subject='Subnet Report', html=email_message, recipients=recipients)

    try:
        mail.send(msg)
    except Exception as e:
        return e

    return 0


@route(app, '/SubnetStatus/get_subnets', methods=['POST'])
@util.workflow_permission_required('SubnetStatus_page')
@util.exception_catcher
def get_subnets():
    networks = []
    if request.form['search_text'] is not None and request.form['search_text'] != '':
        try:
            for n in g.user.get_api().get_by_object_types(request.form['search_text'], ['IP4Block', 'IP4Network', 'IP6Block', 'IP6Network']):
                if '6' in n.get_type():
                    networks.append({'network_id': n.get_id(), 'display_text': n.get_properties()['prefix']})
                else:
                    networks.append({'network_id' : n.get_id(), 'display_text' : n.get_properties()['CIDR']})
        except Exception as e:
            app.loggererror('get_subnets: ' + e.message)

    if len(networks) == 0:
        networks.append({'network_id' : 0, 'display': 'No Subnets Found'})

    return jsonify(networks)


@route(app, '/SubnetStatus/run_stats', methods=['POST'])
@util.rest_workflow_permission_required('SubnetStatus_page')
@util.rest_exception_catcher
def run_stats():
    json_data = request.get_json()

    data = run_stats_common(json_data['subnet_id'])
    if 'email' in json_data:
        email_report(json_data['email'], data['report'])

    return jsonify(data)


@route(app, '/SubnetStatus/get_stats', methods=['POST'])
@util.rest_workflow_permission_required('SubnetStatus_page')
@util.rest_exception_catcher
def get_stats():

    return jsonify(run_stats_common(request.form['subnet_id']))


def run_stats_common(bam_id):
    bam_object = g.user.get_api().get_entity_by_id(str(bam_id))

    if 'Network' in bam_object.get_type():
        return_data = {'network': calculate_network_stats(bam_object)}
    else:
        return_data = {'block': calculate_block_stats(bam_object)}

    report = generate_report(return_data)
    return_data.update({'report': report})

    return return_data


@route(app, '/SubnetStatus/get_network_stats', methods=['POST'])
@util.workflow_permission_required('SubnetStatus_page')
@util.exception_catcher
def get_network_stat():
    network = g.user.get_api().get_entity_by_id(str(request.form['subnet_id']))

    return_data = calculate_network_stats(network)

    return jsonify(return_data)


@route(app, '/SubnetStatus/get_block_stats', methods=['POST'])
@util.workflow_permission_required('SubnetStatus_page')
@util.exception_catcher
def get_block_stat():
    bam_block = g.user.get_api().get_entity_by_id(str(request.form['subnet_id']))

    return_data = calculate_block_stats(bam_block)

    return jsonify(return_data)


def calculate_block_stats(bam_block):
    if bam_block.get_type() == 'IP6Block':
        block_address = bam_block.get_property('prefix')
        block = ipaddress.ip_network(block_address)
    else:
        block_address = bam_block.get_property('CIDR')
        block = ipaddress.ip_network(block_address)
    block_data = {}
    block_data.update({'address_space': block_address})
    block_data.update({'id': bam_block.get_id()})

    total_block_size = block.num_addresses - 2
    block_data.update({'total_size': total_block_size})
    block_data.update({'type': bam_block.get_type()})
    total_free = total_block_size

    if bam_block.get_type() == 'IP4Block':
        for network in bam_block.get_ip4_networks():
            return_data = calculate_network_stats(network)
            total_free -= return_data['total_allocated']
            block_data.update({network.get_property('CIDR'): return_data})

        for found_block in bam_block.get_ip4_blocks():
            return_data = calculate_block_stats(found_block)
            total_free -= return_data['total_allocated']
            block_data.update({found_block.get_property('CIDR'): return_data})

        next_address = bam_block.get_next_available_ip4_address()
        if next_address != '':
            block_data.update({'next_available_address': next_address})
        try:
            next_available = bam_block.get_next_available_ip4_network(256, auto_create=False)
            block_data.update({'next_available_network': next_available})
        except APIException as e:
            # Nothing to do here since we aren't adding anything to the object
            next_available = ''
    else:
        for network in bam_block.get_ip6_networks():
            return_data = calculate_network_stats(network)
            total_free -= return_data['total_allocated']
            block_data.update({network.get_property('prefix'): return_data})

        for found_block in bam_block.get_ip6_blocks():
            return_data = calculate_block_stats(found_block)
            total_free -= return_data['total_allocated']
            block_data.update({found_block.get_property('prefix'): return_data})

    if total_free < total_block_size:
        block_data.update({'percent_free': round((float(total_free) / float(total_block_size)) * 100, 0)})
    else:
        block_data.update({'percent_free': 100})

    block_data.update({'total_free': total_free})
    block_data.update({'total_allocated': total_block_size - total_free})

    return block_data


def calculate_network_stats(bam_network):
    if bam_network.get_type() == 'IP4Network':
        network_address = bam_network.get_property('CIDR')
        network = ipaddress.ip_network(network_address)
    else:
        network_address = bam_network.get_property('prefix')
        network = ipaddress.ip_network(network_address)
    network_data = {}
    network_data.update({'address_space': network_address})
    network_data.update({'id': bam_network.get_id()})

    total_network_size = network.num_addresses - 2
    network_data.update({'total_size': total_network_size})
    network_data.update({'type': bam_network.get_type()})
    total_free = total_network_size

    if bam_network.get_type() == 'IP4Network':
        for n in bam_network.get_children_of_type('IP4Address'):
            total_free = total_free - 1
            if n.get_property('state') == 'GATEWAY':
                network_data.update({'gateway': n.get_address()})

        for d in bam_network.get_children_of_type('DHCP4Range'):
            network_data.update({'dhcp_start': d.get_property('start')})
            network_data.update({'dhcp_end': d.get_property('end')})

        next_address = bam_network.get_next_available_ip4_address()
        if next_address != '':
            network_data.update({'next_available_address': next_address})
    else:
        for n in bam_network.get_children_of_type('IP6Address'):
            total_free = total_free - 1
            if n.get_property('state') == 'GATEWAY':
                network_data.update({'gateway': n.get_address()})

        for d in bam_network.get_children_of_type('DHCP6Range'):
            network_data.update({'dhcp_start': d.get_property('start')})
            network_data.update({'dhcp_end': d.get_property('end')})

    if total_free < total_network_size:
        network_data.update({'percent_free': round((float(total_free) / float(total_network_size)) * 100, 0)})
    else:
        network_data.update({'percent_free': 100})

    network_data.update({'total_free': total_free})
    network_data.update({'total_allocated': total_network_size - total_free})

    return network_data


def generate_report(json_data):

    report = """<p>Report of the requested subnet <br></p>"""

    for key, data in list(json_data.items()):
        if isinstance(data, dict):
            report += subnet_data_generate(data, 0)

    report += """<script>
                    function myFunction(div_id) {
                        var x = document.getElementById(div_id);
                        if (x.style.display === "none") {
                            x.style.display = "block";
                        } else {
                            x.style.display = "none";
                        }
                    }
                </script>"""

    return report


def subnet_data_generate(json_data, indent):
    color = 'green'
    if json_data['percent_free'] <= 20 and json_data['percent_free'] > 10:
        color = 'yellow'
    elif json_data['percent_free'] <= 10:
        color = 'red'

    subnet_report = """<br><div style="margin-left: %spx;border-style: solid;">
    <b> Address Space: </b>  <font color="green">%s</font> <br>
    <b> Type: </b>  <font color="green">%s</font> <br>
    <b> Total Size: </b> <font color="green">%s</font> <br><br>
    <b>Utilization </b> <br>
    <div style="width:%s;background-color:grey" id="progress"><div id="progressBar" style="width:%s;background-color:%s">%s</div></div>
    <b> Total Allocated: </b> <font color="%s">%s</font> <br>
    <b> Total Free: </b> <font color="%s">%s</font> <br>""" \
                             % (indent, json_data['address_space'], json_data['type'], str(json_data['total_size']),
                                '100%', str(100 - json_data['percent_free']) + '%', color,
                                str(100 - json_data['percent_free']) + '%', color,
                                str(json_data['total_allocated']), color, str(json_data['total_free']))
    if 'next_available_network' in json_data:
        subnet_report += """<br><b> Next Available Network: </b>  <font color="green">%s</font>""" %\
                         json_data['next_available_network']
    if 'next_available_address' in json_data:
        subnet_report += """<br><b> Next Available Address: </b>  <font color="green">%s</font>""" \
                         % json_data['next_available_address']
    if 'gateway' in json_data:
        subnet_report += """<br><b> Gateway: </b>  <font color="green">%s</font>""" % json_data['gateway']
    if 'dhcp_start' in json_data:
        subnet_report += """<br><b> DHCP Range: </b>  <font color="green">%s - %s</font>""" % \
                         (json_data['dhcp_start'], json_data['dhcp_end'])
    if 'Network' not in json_data['type']:
        subnet_report += """<br><button type="button" onclick="myFunction('div_%s')" class="btn-primary">Show/Hide Children</button></div>""" % str(json_data['id'])
        subnet_report += """<div id="div_%s">""" % str(json_data['id'])
        for key, data in list(json_data.items()):
            if isinstance(data, dict):
                subnet_report += subnet_data_generate(data, indent+40)
        subnet_report += """</div>"""
    else:
        subnet_report += """</div>"""
    return subnet_report
