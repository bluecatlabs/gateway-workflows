# Copyright 2017 BlueCat Networks. All rights reserved.
"""
Useful Functions
"""
from flask import g


def get_groups(default_val=False):
    """
    Get a list of user groups for display in a dropdown box.

    :return: List of group ID, group name tuples.
    """
    result = []
    if g.user:
        if default_val:
            result.append(('1', 'Please Select'))
            groups = g.user.get_api().get_by_object_types('*', ['UserGroup'])
        for gr in groups:
            result.append((gr.get_id(), gr.get_name()))
    return result