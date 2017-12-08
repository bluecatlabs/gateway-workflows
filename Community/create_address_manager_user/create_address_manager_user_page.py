# Copyright 2017 BlueCat Networks (USA) Inc. and its affiliates
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# By: Bill Morton (bmorton@bluecatnetworks.com)
# Date: 06-12-2017
# Gateway Version: 17.10.1


# Copyright 2017 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys

from flask import url_for, redirect, render_template, flash, g

from bluecat import route, util
import config.default_config as config
from main_app import app
from .create_address_manager_user_form import GenericFormTemplate
from bluecat.user import User


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(unicode(__file__, encoding)))

#This is a check to see if the user exists
def doesUserExsist(userName):
    if g.user:
        try:
            userId = g.user.get_api().get_user(userName)
            if userId:
                return True
        except:
            return False

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
@route(app, '/create_address_manager_user/create_address_manager_user_endpoint')
@util.workflow_permission_required('create_address_manager_user_page')
@util.exception_catcher
def create_address_manager_user_create_address_manager_user_page():
    form = GenericFormTemplate()
    form.usergroups.choices = get_user_groups()

    return render_template(
        'create_address_manager_user_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/create_address_manager_user/form', methods=['POST'])
@util.workflow_permission_required('create_address_manager_user_page')
@util.exception_catcher
def create_address_manager_user_create_address_manager_user_page_form():
    form = GenericFormTemplate()
    form.usergroups.choices = get_user_groups()

    if form.validate_on_submit():

        try:
            # Check to see if the user exists
            userExist = doesUserExsist(form.username.data)

            #If the user exists then we return error in GUI and reload the form
            if userExist == True:
                flash('User ' + form.username.data + ' already exists in Address Manager!')
                form = GenericFormTemplate()
                form.usergroups.choices = get_user_groups()

            # If the user dosen't exist and the form has all req fields entered create user.
            # This is only for Admins. We dont need the Security and History privilege.
            elif userExist == False and form.typeofuser.data == 'ADMIN':
                #setting the properties for a one time add and not update one by one
                properties = 'phoneNumber=' + form.phonenumber.data + '|PortalGroup=' + form.gateway_groups.data + '|userType=' + form.typeofuser.data

                #Creating the user with the properties above
                usr = g.user.get_api().add_user(form.username.data, form.password.data, form.email.data, form.acctype.data, properties)

                #grpnames = list()

                #Adding groups to the user but has to have one or more group selection
                if form.usergroups.data:
                    for group_id in form.usergroups.data:
                        User.add_to_group(usr, group_id)
                        #grpnames.append(g.user.get_api().get_entity_by_id(int(group_id)).get_name())

                # Logging sent to the session log file
                g.user.logger.info('SUCCESS - Created admin user' + form.username.data)
                # Message on the form
                flash('Success - Created and Admin user: ' + form.username.data, 'succeed')

            elif userExist == False and form.typeofuser.data == 'REGULAR':
                # This is only for non-administrators. We DO need the Security and History privilege.
                properties = 'phoneNumber=' + form.phonenumber.data + '|PortalGroup=' + form.gateway_groups.data + '|userType=' + form.typeofuser.data + '|securityPrivilege=' + form.secpriv.data + '|historyPrivilege=' + form.histpriv.data
                usr = g.user.get_api().add_user(form.username.data, form.password.data, form.email.data,
                                                form.acctype.data, properties)
                #grpnames = list()

                #Adding groups to the user but has to have one or more group selection
                if form.usergroups.data:
                    for group_id in form.usergroups.data:
                        User.add_to_group(usr, group_id)
                        #grpnames.append(g.user.get_api().get_entity_by_id(int(group_id)).get_name())

                # Logging sent to the session log file
                g.user.logger.info('SUCCESS - Created non-admin user' + form.username.data)
                # Message on the form
                flash('Success - Created a Non-Admin user:  ' + form.username.data, 'succeed')

            return redirect(url_for('create_address_manager_usercreate_address_manager_user_create_address_manager_user_page'))

        except Exception as e:
            flash(util.safe_str(e))
            # Log error and render workflow page
            g.user.logger.warning('%s' % util.safe_str(e), msg_type=g.user.logger.EXCEPTION)
            return render_template('create_address_manager_user_page.html',
                                   form=form,
                                   text=util.get_text(module_path(), config.language),
                                   options=g.user.get_options())

    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'create_address_manager_user_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )