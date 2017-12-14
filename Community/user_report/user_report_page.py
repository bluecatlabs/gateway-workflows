#Copyright 2017 BlueCat Networks (USA) Inc. and its affiliates
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#http://www.apache.org/licenses/LICENSE-2.0
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
#By: Bill Morton (bmorton@bluecatnetworks.com)
#Date: 06-12-2017
#Gateway Version: 17.10.1

# Copyright 2017 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys
import csv
import datetime
import time

from flask import render_template, flash, g

from bluecat import route, util, entity
import config.default_config as config
from main_app import app
from .user_report_form import GenericFormTemplate
from werkzeug.utils import secure_filename

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(unicode(__file__, encoding)))

# Get a list of Groups for display in a dropdown box.
def get_user_groups():
    result = []
    if g.user:
        groups = g.user.get_api().get_by_object_types('*', ['UserGroup'])
        for gr in groups:
            result.append((gr.get_id(), gr.get_name()))
    return result

# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/user_report/user_report_endpoint')
@util.workflow_permission_required('user_report_page')
@util.exception_catcher
def user_report_user_report_page():
    form = GenericFormTemplate()
    form.usergroups.choices = get_user_groups()

    return render_template(
        'user_report_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/user_report/form', methods=['POST'])
@util.workflow_permission_required('user_report_page')
@util.exception_catcher
def user_report_user_report_page_form():
    form = GenericFormTemplate()
    form.usergroups.choices = get_user_groups()

    try:
        #Generating the data
        reportfile = generate_report(form.reporttype.data, form.usergroups.data)

        # Logging sent to the session log file
        g.user.logger.info('Ran user report ' + form.reporttype.data + ' generated file: ' + reportfile)

        # Message on the form
        flash(' Success - Ran user report ' + form.reporttype.data + '. Generated file: ' + reportfile, 'succeed')

        #Setting the URL based off the config file and removing the services part
        report = '/bluecat_portal/resources/reports/' + reportfile

        return render_template(
            'user_report_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
            ref=report
        )

    except Exception as e:
        flash(util.safe_str(e))
        # Log error and render workflow page
        g.user.logger.warning('%s' % util.safe_str(e), msg_type=g.user.logger.EXCEPTION)
        return render_template('user_report_page.html',
                               form=form,
                               text=util.get_text(module_path(), config.language),
                               options=g.user.get_options())

def generate_report(reporttype, bamusergroup):
    result = []
    #Setting the time and date format for the file we are generating
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')

    #Setting the directory on the server to put the report
    report_dir = 'bluecat_portal/resources/reports'

    if reporttype == 'GUI':
        #Setting the report header
        result.append(
            ['User Login', 'Email Address', 'Phone Number', 'History Privilege', 'Security Privilege', 'Access Type',
             'User Type', 'Gateway Groups'])

        gui_users = g.user.get_api().get_by_object_types('*', 'User')

        for user in gui_users:

            if user.get_property('userAccessType') == 'GUI':
                username = user.get_name()
                email = user.get_property('email')
                phone = user.get_property('phoneNumber')
                history = user.get_property('historyPrivilege')
                security = user.get_property('securityPrivilege')
                access_type = user.get_property('userAccessType')
                user_type = user.get_property('userType')
                portal_group = user.get_property('PortalGroup')

                result.append(
                    [username, email, phone, history, security, access_type, user_type, portal_group])
        #Creating filename
        report_file = 'gateway-user-report-all-users-gui-' + st + '.csv'

        filename = os.path.join(report_dir, secure_filename(report_file))

        with open(filename, 'wb') as myreportfile:
            writer = csv.writer(myreportfile, lineterminator='\n')
            writer.writerows(result)

    elif reporttype == 'API':
        # Setting the report header
        result.append(
            ['User Login', 'Email Address', 'Phone Number', 'History Privilege', 'Security Privilege', 'Access Type',
             'User Type', 'Gateway Groups'])

        gui_users = g.user.get_api().get_by_object_types('*', 'User')

        for user in gui_users:

            if user.get_property('userAccessType') == 'API':
                username = user.get_name()
                email = user.get_property('email')
                phone = user.get_property('phoneNumber')
                history = user.get_property('historyPrivilege')
                security = user.get_property('securityPrivilege')
                access_type = user.get_property('userAccessType')
                user_type = user.get_property('userType')
                portal_group = user.get_property('PortalGroup')

                result.append(
                    [username, email, phone, history, security, access_type, user_type, portal_group])
        # Creating filename
        report_file = 'gateway-user-report-all-users-api-' + st + '.csv'

        filename = os.path.join(report_dir, secure_filename(report_file))

        with open(filename, 'wb') as myreportfile:
            writer = csv.writer(myreportfile, lineterminator='\n')
            writer.writerows(result)

    elif reporttype == 'GUI_AND_API':
        # Setting the report header
        result.append(
            ['User Login', 'Email Address', 'Phone Number', 'History Privilege', 'Security Privilege', 'Access Type',
             'User Type', 'Gateway Groups'])

        gui_users = g.user.get_api().get_by_object_types('*', 'User')

        for user in gui_users:

            if user.get_property('userAccessType') == 'GUI_AND_API':
                username = user.get_name()
                email = user.get_property('email')
                phone = user.get_property('phoneNumber')
                history = user.get_property('historyPrivilege')
                security = user.get_property('securityPrivilege')
                access_type = user.get_property('userAccessType')
                user_type = user.get_property('userType')
                portal_group = user.get_property('PortalGroup')

                result.append(
                    [username, email, phone, history, security, access_type, user_type, portal_group])
        # Creating filename
        report_file = 'gateway-user-report-all-users-gui-and_api-' + st + '.csv'

        filename = os.path.join(report_dir, secure_filename(report_file))

        with open(filename, 'wb') as myreportfile:
            writer = csv.writer(myreportfile, lineterminator='\n')
            writer.writerows(result)

    elif reporttype == 'BY_GROUPS':
        # Setting the report header
        result.append(
            ['User Login', 'Email Address', 'Phone Number', 'History Privilege', 'Security Privilege', 'Access Type',
             'User Type', 'Gateway Groups'])

        grpId = g.user.get_api().get_entity_by_id(bamusergroup)
        usrInGrp = entity.Entity.get_linked_entities(grpId, 'User')

        for user in usrInGrp:
            group_list = []

            username = user.get_name()
            email = user.get_property('email')
            phone = user.get_property('phoneNumber')
            history = user.get_property('historyPrivilege')
            security = user.get_property('securityPrivilege')
            access_type = user.get_property('userAccessType')
            user_type = user.get_property('userType')
            portal_group = user.get_property('PortalGroup')

            result.append([username, email, phone, history, security, access_type, user_type, portal_group])
        # Creating filename
        report_file = 'gateway-user-report-by-group-' + st + '.csv'

        filename = os.path.join(report_dir, secure_filename(report_file))

        with open(filename, 'wb') as myreportfile:
            writer = csv.writer(myreportfile, lineterminator='\n')
            writer.writerows(result)

    elif reporttype == 'ALL_USERS':
        # Setting the report header
        result.append(
            ['User Login', 'Email Address', 'Phone Number', 'History Privilege', 'Security Privilege', 'Access Type',
             'User Type', 'Groups', 'Gateway Groups'])

        all_users = g.user.get_api().get_by_object_types('*', 'User')

        for user in all_users:
            group_list = []

            username = user.get_name()
            email = user.get_property('email')
            phone = user.get_property('phoneNumber')
            history = user.get_property('historyPrivilege')
            security = user.get_property('securityPrivilege')
            access_type = user.get_property('userAccessType')
            user_type = user.get_property('userType')
            portal_group = user.get_property('PortalGroup')
            usr_id = user.get_id()

            groups = user.get_linked_entities('UserGroup')

            for group in groups:
                group_list.append(group.get_name())

            result.append([username, email, phone, history, security, access_type, user_type, group_list, portal_group])
        # Creating filename
        report_file = 'gateway-user-report-all-users-' + st + '.csv'

        filename = os.path.join(report_dir, secure_filename(report_file))

        with open(filename, 'wb') as myreportfile:
            writer = csv.writer(myreportfile, lineterminator='\n')
            writer.writerows(result)

    return report_file