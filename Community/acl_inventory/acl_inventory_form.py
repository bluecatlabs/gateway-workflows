# Copyright 2020 BlueCat Networks. All rights reserved.
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomSubmitField
from .acl_inventory_wtform_fields import ACL


class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'acl_inventory'
    workflow_permission = 'acl_inventory_page'

    acls_list = ACL(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='ACL List',
        required=True,
        coerce=int,
        is_disabled_on_start=False,
        clear_below_on_change=False
    )

    download = CustomSubmitField(
        label='Download',
        is_disabled_on_start=False
    )
