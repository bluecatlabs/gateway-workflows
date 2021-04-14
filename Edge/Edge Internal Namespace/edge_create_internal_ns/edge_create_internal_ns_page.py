# Copyright 2020 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys

from flask import url_for, redirect, render_template, flash, g

from bluecat import route, util
import config.default_config as config
from main_app import app
from .edge_create_internal_ns_form import GenericFormTemplate
from bluecat_portal.customizations.edge import edge
from ..edge_create_internal_ns_config import edge_create_internal_ns_configuration


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/edge_create_internal_ns/edge_create_internal_ns_endpoint')
@util.workflow_permission_required('edge_create_internal_ns_page')
@util.exception_catcher
def edge_create_internal_ns_edge_create_internal_ns_page():
    form = GenericFormTemplate()

    return render_template(
        'edge_create_internal_ns_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/edge_create_internal_ns/form', methods=['POST'])
@util.workflow_permission_required('edge_create_internal_ns_page')
@util.exception_catcher
def edge_create_internal_ns_edge_create_internal_ns_page_form():
    form = GenericFormTemplate()

    if form.validate_on_submit():
        # Login to Edge
        edge_session = edge(edge_create_internal_ns_configuration.edge_url, edge_create_internal_ns_configuration.client_id, edge_create_internal_ns_configuration.clientSecret)
        if edge_session.get_session_status() is False:
            exit()
        else:
            print("Contacted the Edge")

        # Find the domain list ID
        new_dl = False
        try:
            # Create the Domain List if it doesn't exist
            dl = edge_session.make_new_domain_list(form.domainlist_name.data, form.domainlist_desc.data)
            edge_id = dl['id']
            new_dl = True
        except Exception as e:
            # Find the ID of the Domain List if it already exists
            domain_lists = edge_session.list_dl()
            for dl in domain_lists:
                if dl['name'] == form.domainlist_name.data:
                    edge_id = dl['id']
                    break

        zone_list = []

        #Get all zones (Need to filter out non internal)
        zones = g.user.get_api().get_by_object_types('*', 'Zone')
        for zone in zones:
            # This is to speed up the code.
            zone_list.append(zone)

        zone_file_list = ['',]
        for zone in zone_list:
            if zone.get_property('deployable') == 'true':
                if zone.get_configuration().get_name() == edge_create_internal_ns_configuration.default_configuration:
                    # Trying to get only the correct views zones below
                    parent_type = zone.get_parent()._api_entity['type']
                    parent = zone.get_parent()
                    while parent_type != 'View':
                        parent_type = []
                        parent_type = parent.get_parent()._api_entity['type']
                        parent = parent.get_parent()
                        continue
                    # Need to match the view in the config
                    if parent.get_name() == edge_create_internal_ns_configuration.default_view:
                        zone_file_list.append(zone.get_property('absoluteName'))

        with open(edge_create_internal_ns_configuration.domain_list_file, 'w') as f:
            f.writelines("%s\n" % place for place in zone_file_list)

        new_dl_list = edge_session.push_file(edge_id, edge_create_internal_ns_configuration.domain_list_file)

        if form.namespaces:
            namespaceid_start = form.namespaces.data.rfind('(') + 1
            namespaceid_end = form.namespaces.data.rfind(')', namespaceid_start)
            namespace_id = form.namespaces.data[namespaceid_start:namespaceid_end]

            edge_session.update_namespace_domain_list(namespace_id, [edge_id])

        # Put form processing code here
        if new_dl:
            g.user.logger.info('Created Internal  Namespace: ' + dl['name'] + ' added: ' + str(new_dl_list['numOfValidDomains']) + ' Zones')
            flash('Created Internal  Namespace: ' + dl['name'] + ' added: ' + str(new_dl_list['numOfValidDomains']) + ' Zones' , 'succeed')
        else:
            g.user.logger.info('Updated Internal  Namespace: ' + dl['name'] + ' added: ' + str(new_dl_list['numOfValidDomains']) + ' Zones')
            flash('Updated Internal  Namespace: ' + dl['name'] + ' added: ' + str(new_dl_list['numOfValidDomains']) + ' Zones' , 'succeed')
        return redirect(url_for('edge_create_internal_nsedge_create_internal_ns_edge_create_internal_ns_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'edge_create_internal_ns_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
