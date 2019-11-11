# Copyright 2019 BlueCat Networks. All rights reserved.
from bluecat.wtform_fields import SimpleAutocompleteField, ValidatingStringField
# Import Javascript Helpers
from bluecat.ui_components.wtform_widgets import SuperSelect
from bluecat.wtform_fields.custom_string_field import CustomStringField
from.edge_create_internal_ns_logic import get_edge_namespaces_endpoint


class EdgeNamespaces(SimpleAutocompleteField):
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
            label = 'Edge Namespaces'
        super(EdgeNamespaces, self).__init__(label,
                                   validators,
                                   server_side_method=get_edge_namespaces_endpoint,
                                   result_decorator=result_decorator,
                                   **kwargs)
