# Copyright 2019 BlueCat Networks. All rights reserved.
from bluecat.wtform_fields import SimpleAutocompleteField
from .bulk_record_export_endpoints import get_ip4_networks_endpoint


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
