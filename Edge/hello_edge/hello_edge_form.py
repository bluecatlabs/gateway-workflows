# Copyright 2019 BlueCat Networks. All rights reserved.

from wtforms import SubmitField
from wtforms.validators import DataRequired, URL
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomStringField


class EdgeForm(GatewayForm):

    workflow_name = 'hello_edge'
    workflow_permission = 'hello_edge_page'

    edge = CustomStringField(
        label='Edge CI',
        default='https://api.edge.example.com',
        validators=[DataRequired(), URL()],
        is_disabled_on_start=False
    )

    client = CustomStringField(
        label='Client ID',
        default='',
        validators=[DataRequired()],
        is_disabled_on_start=False
    )

    client_secret = CustomStringField(
        label='Client Secret',
        default='',
        validators=[DataRequired()],
        is_disabled_on_start=False
    )


    submit = SubmitField(label='Submit')
