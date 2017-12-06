# Copyright 2017 BlueCat Networks. All rights reserved.

import datetime

from wtforms import StringField, PasswordField, SelectField, FileField, RadioField, BooleanField, DateTimeField, SubmitField, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired, Email, MacAddress, IPAddress, URL
from bluecat.wtform_extensions import GatewayForm, validate_element_in_tuple
from bluecat.wtform_fields import *

class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'create_address_manager_user'
    workflow_permission = 'create_address_manager_user_page'

    username = CustomStringField(
        label='Username',
        is_disabled_on_start=False,
        required=True,
        validators=[]
    )

    password = PasswordField(
        label='Password',
        validators=[DataRequired()]
    )

    email = CustomStringField(
        label='Email Address',
        is_disabled_on_start=False,
        required=True,
        validators=[DataRequired(), Email()]
    )

    phonenumber = CustomStringField(
        label='Phone Number',
        is_disabled_on_start=False,
        required=False,
    )

    typeofuser = CustomSelectField(
        label='Type of User',
        is_disabled_on_start=False,
        # Below are the API values followed by GUI values
        choices=[('ADMIN', 'Administrator'), ('REGULAR', 'Non-Administrator')],
        clear_below_on_change=False,
        #Javascript call below to enable/disable secpriv and histpriv
        on_complete = ['is_admin']
    )

    secpriv = NoPreValidationSelectField(
        label='Security Privilege',
        # Below are the API values followed by GUI values
        choices=[ ('NO_ACCESS', 'No Access'), ('VIEW_MY_ACCESS_RIGHTS', 'View My Access Rights'), ('VIEW_OTHERS_ACCESS_RIGHTS', 'View Others Access Rights'), ('CHANGE_ACCESS_RIGHTS', 'Change Access Rights'), ('ADD_ACCESS_RIGHTS', 'Add Access Rights'), ('DELETE_ACCESS_RIGHTS', 'Delete Access Rights')]
    )

    histpriv = NoPreValidationSelectField(
        label='History Privilege',
        # Below are the API values followed by GUI values
        choices=[('HIDE', 'Hide'), ('VIEW_HISTORY_LIST', 'View History List')]
    )

    acctype = CustomSelectField(
        label='Access Type',
        # Below are the API values followed by GUI values
        choices=[('GUI', 'GUI'), ('API', 'API'), ('GUI_AND_API', 'GUI And API')],
        clear_below_on_change=False,
        is_disabled_on_start=False
    )

    #List of all Gateway groups (UDFs) for users manually, no API
    gateway_groups = CustomSelectField(
        label='Assign to Gateway Group',
        required=False,
        # Below are the UDF values for workflow permissions followed by GUI values
        choices=[('admin', 'admin'), ('all', 'all')],
        clear_below_on_change=False,
        is_disabled_on_start=False,
        result_decorator = None
    )

    #List of all Address Manager Groups by API
    usergroups = SelectMultipleField(
        'Assign to Groups',
        coerce=int
    )

    submit = SubmitField(label='Submit')