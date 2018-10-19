# Copyright 2018 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
import datetime
import re
import json
import os
from wtforms import StringField, PasswordField, FileField
from wtforms import BooleanField, DateTimeField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, MacAddress, URL, ValidationError
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, IP4Address

states = [
    ["AL", "Alabama"],
    ["AK", "Alaska"],
    ["AS", "American Samoa"],
    ["AZ", "Arizona"],
    ["AR", "Arkansas"],
    ["CA", "California"],
    ["CO", "Colorado"],
    ["CT", "Connecticut"],
    ["DE", "Delaware"],
    ["DC", "District Of Columbia"],
    ["FM", "Federated States Of Micronesia"],
    ["FL", "Florida"],
    ["GA", "Georgia"],
    ["GU", "Guam"],
    ["HI", "Hawaii"],
    ["ID", "Idaho"],
    ["IL", "Illinois"],
    ["IN", "Indiana"],
    ["IA", "Iowa"],
    ["KS", "Kansas"],
    ["KY", "Kentucky"],
    ["LA", "Louisiana"],
    ["ME", "Maine"],
    ["MH", "Marshall Islands"],
    ["MD", "Maryland"],
    ["MA", "Massachusetts"],
    ["MI", "Michigan"],
    ["MN", "Minnesota"],
    ["MS", "Mississippi"],
    ["MO", "Missouri"],
    ["MT", "Montana"],
    ["NE", "Nebraska"],
    ["NV", "Nevada"],
    ["NH", "New Hampshire"],
    ["NJ", "New Jersey"],
    ["NM", "New Mexico"],
    ["NY", "New York"],
    ["NC", "North Carolina"],
    ["ND", "North Dakota"],
    ["MP", "Northern Mariana Islands"],
    ["OH", "Ohio"],
    ["OK", "Oklahoma"],
    ["OR", "Oregon"],
    ["PW", "Palau"],
    ["PA", "Pennsylvania"],
    ["PR", "Puerto Rico"],
    ["RI", "Rhode Island"],
    ["SC", "South Carolina"],
    ["SD", "South Dakota"],
    ["TN", "Tennessee"],
    ["TX", "Texas"],
    ["UT", "Utah"],
    ["VT", "Vermont"],
    ["VI", "Virgin Islands"],
    ["VA", "Virginia"],
    ["WA", "Washington"],
    ["WV", "West Virginia"],
    ["WI", "Wisconsin"],
    ["WY", "Wyoming"]
]
state_choices = [(x[0], x[1]) for x in states]
default = [("-1","Please Select")]
state_choices = default + state_choices


def validate_name(form, field):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/rules.json') as f:
        data = json.load(f)

    s = data['network_name']['regex']
    message = data['network_name']['message']
    regex = re.compile(r'%s' % s)
    match = regex.match(field.data)

    try:
        print match.group(0)
    except:
        raise ValidationError(message)


def validate_dropdown(form, field):

    if field.data == '-1':
        raise ValidationError("You need to select an option")


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'network_manager'
    workflow_permission = 'network_manager_page'

    network_name = StringField(
        label='Name',
        validators=[validate_name]
    )

    network_location = SelectField(
        label='Location',
        choices=state_choices,
        validators=[validate_dropdown]
    )

    network_size = SelectField(
        label="Size",
        choices=[('-1','Please Select'), ('256','256'), ('512','512'), ('1024','1024')],
        validators=[validate_dropdown]
    )

    submit = SubmitField(
        label='Submit'
    )




