# Copyright 2020 BlueCat Networks. All rights reserved.
from bluecat.wtform_fields import SimpleAutocompleteField, ValidatingStringField
from .service_request_host_endpoints import get_zones_endpoint, get_ip4_networks_endpoint, get_ip4_address_endpoint


class CustomZone(SimpleAutocompleteField):
    """
    Autocomplete enabled field for Zone entities.

    :param label: HTML label for the generated field.
    :param validators: WTForm validators for the field run on the server side.
    :param kwargs: Other keyword arguments for WTForms Fields.

    """
    def __init__(self, label='Zone', validators=None, result_decorator=None, **kwargs):
        """ Pass parameters to SimpleAutocompleteField for initialization.
        """
        super(CustomZone, self).__init__(
            label,
            validators,
            server_side_method=get_zones_endpoint,
            result_decorator=result_decorator,
            **kwargs)


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



class CustomIP4Address(ValidatingStringField):
    """
    StringField for inputting IPv4 addresses with client-side validation
    and auto-checks that it is available.

    :param label: HTML label for the generated field.
    :param validators: WTForm validators for the field run on the server side.
    :param result_decorator: Function to manipulate result set instead of a server-side call.
    :param kwargs: Other keyword arguments for WTForms Fields.

    """
    def __init__(self, label='IP Address', validators=None, result_decorator=None, **kwargs):
        """ Pass parameters to ValidatingStringField for initialization.
        """
        super(CustomIP4Address, self).__init__(
            label,
            validators,
            client_side_validator='valid_ip4_address',
            server_side_method=get_ip4_address_endpoint,
            result_decorator=result_decorator,
            **kwargs
        )
