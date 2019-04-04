# Copyright 2019 BlueCat Networks. All rights reserved.
from bluecat.wtform_fields import CustomSelectField
from .acl_inventory_server_endpoints import get_acls


class ACL(CustomSelectField):
    """
    Selectfield enabled field for ACL entities.
    """
    def __init__(self, label='', validators=None, result_decorator=None, **kwargs):
        """
        Pass parameters to Selectfield for initialization.

        :param label: HTML label for the generated field.
        :param validators: WTForm validators for the field run on the server side.
        :param kwargs: Other keyword arguments for WTForms Fields.
        """

        if not label:
            label = 'ACL'
        super(ACL, self).__init__(label,
                                  validators,
                                  choices_function=get_acls,
                                  result_decorator=result_decorator,
                                  **kwargs)
