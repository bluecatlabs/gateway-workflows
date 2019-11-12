# Copyright 2019 BlueCat Networks. All rights reserved.
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
    workflow_name = 'move_to_bluecatgateway_udf'
    workflow_permission = 'move_to_bluecatgateway_udf_page'

    submit = CustomSubmitField(
        label='Submit',
        is_disabled_on_start=False
    )
