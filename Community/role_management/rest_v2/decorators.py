# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
import functools
from flask import g, make_response, jsonify

from .api import RESTv2


def rest_v2_handler(func):
    """
    Decorator to require a permission to access an endpoint or function.

    .. versionadded:: 22.11.1
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user:
            return make_response(jsonify({"message": "Authentication is required."}), 401)

        if not hasattr(g.user, 'v2') or not g.user.v2.is_authenticated:
            g.user.v2 = RESTv2()
        return func(*args, **kwargs)

    return wrapper
