# Copyright 2019 BlueCat Networks. All rights reserved.
from bluecat.wtform_fields import SimpleAutocompleteField
from .add_mac_address_server_endpoints import get_mac_pools_endpoint


class MACPool(SimpleAutocompleteField):
    """
    Autocomplete enabled field for MACPool entities.

    :param label: HTML label for the generated field.
    :param validators: WTForm validators for the field run on the server side.
    :param kwargs: Other keyword arguments for WTForms Fields.

    """
    def __init__(self, label='MAC Pool', validators=None, result_decorator=None, **kwargs):
        """ Pass parameters to SimpleAutocompleteField for initialization.
        """
        super(MACPool, self).__init__(label,
                                      validators,
                                      server_side_method=get_mac_pools_endpoint,
                                      result_decorator=result_decorator,
                                      **kwargs)
