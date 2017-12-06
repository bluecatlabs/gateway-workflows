# Copyright 2017 BlueCat Networks. All rights reserved.
"""
Custom WTForm fields.
"""

from bluecat.ui_components.wtform_widgets import SuperSelect

from .util_custom import get_groups
from bluecat.wtform_fields import CustomSelectField

class Group(CustomSelectField):
    """
    SelectField that is autopopulated with group data.
    """
    widget = SuperSelect()

    def __init__(self, label=None, validators=None, **kwargs):
        if not label:
            label = 'Group'
        super(Group, self).__init__(label=label, validators=validators,
                                            choices_function=get_groups,
                                            **kwargs)