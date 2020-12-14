# Copyright 2020 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomSubmitField


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'dump_data'
    workflow_permission = 'dump_data_page'

    submit = CustomSubmitField(label='Submit',
                               is_disabled_on_start=False)
