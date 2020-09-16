# Copyright 2020 BlueCat Networks. All rights reserved.
from bluecat.wtform_fields import SimpleAutocompleteField, ValidatingStringField
from .add_dual_stack_host_logic import get_ip6_address_endpoint
# Import Javascript Helpers
from bluecat.ui_components.wtform_widgets import SuperSelect
from bluecat.wtform_fields.custom_string_field import CustomStringField

class IP6Address(ValidatingStringField):
    """
    StringField for inputting IPv6 addresses with client-side validation
    and auto-checks that the network exists.

    :param label: HTML label for the generated field.
    :param validators: WTForm validators for the field run on the server side.
    :param result_decorator: Function to manipulate result set instead of a server-side call.
    :param kwargs: Other keyword arguments for WTForms Fields.

    """
    def __init__(self, label='IPv6 Address', validators=None, result_decorator=None, **kwargs):
        """ Pass parameters to ValidatingStringField for initialization.
        """
        super(IP6Address, self).__init__(
            label,
            validators,
            client_side_validator='valid_ip6_address',
            server_side_method=get_ip6_address_endpoint,
            result_decorator=result_decorator,
            **kwargs
        )
