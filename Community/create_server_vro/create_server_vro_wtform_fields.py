# Copyright 2020 BlueCat Networks. All rights reserved.
from bluecat.wtform_fields import SimpleAutocompleteField, ValidatingStringField
from .create_server_vro_logic import get_ip4_networks_endpoint
# Import Javascript Helpers
from bluecat.ui_components.wtform_widgets import SuperSelect
from bluecat.wtform_fields.custom_string_field import CustomStringField


class IP4Network(SimpleAutocompleteField):
    """
    Autocomplete enabled field to retrieve networks by hint
    """
    def __init__(self, label='', validators=None, result_decorator=None, **kwargs):
        """
        Pass parameters to SimpleAutocompleteField for initialization.

        :param label: HTML label for the generated field.
        :param validators: WTForm validators for the field run on the server side.
        :param kwargs: Other keyword arguments for WTForms Fields.
        """

        if not label:
            label = 'IP4Network'
        super(IP4Network, self).__init__(label,
                                   validators,
                                   server_side_method=get_ip4_networks_endpoint,
                                   result_decorator=result_decorator,
                                   **kwargs)
